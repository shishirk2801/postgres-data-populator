package main

import (
    "bytes"
    "context"
    "database/sql"
    "fmt"
    "net/http"
    "os"
    "sync"
    "time"
    
    "github.com/xuri/excelize/v2"
    _ "github.com/lib/pq"
)

type RowData struct {
    rowNum int
    data   []interface{}
}

func main() {
    // Take presigned URL as command line argument
    if len(os.Args) < 2 {
        fmt.Println("Please provide the presigned URL as an argument")
    }
    presignedURL := os.Args[1]

    // Database connection string
    connStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
        "localhost", 5432, "user", "password", "test_db")
    
    // Connect to database
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        fmt.Println("Failed to connect to database:", err)
    }
    defer db.Close()

    // Set connection pool settings
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(5)
    db.SetConnMaxLifetime(time.Minute * 5)

    // Create new XLSX file in memory
    f := excelize.NewFile()
    defer func() {
        if err := f.Close(); err != nil {
            fmt.Println(err)
        }
    }()

    // Query data in batches
    const batchSize = 50000
    sheetName := "Sheet1"
    
    // Write headers based on table schema
    headers := []string{"ID", "Column1", "Column2", "Column3", "Column4", "Column5", 
                       "Column6", "Column7", "Column8", "Column9", "Column10"}

    // Create streaming writer
    streamWriter, err := f.NewStreamWriter(sheetName)
    if err != nil {
        fmt.Println("Failed to create stream writer:", err)
        return
    }

    // Write headers using stream writer
    headerRow := make([]interface{}, len(headers))
    for i, header := range headers {
        headerRow[i] = header
    }
    if err := streamWriter.SetRow("A1", headerRow); err != nil {
        fmt.Println("Failed to write headers:", err)
        return
    }

    // Prepare the query statement
    stmt, err := db.Prepare(`
        SELECT id, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10
        FROM test_table 
        ORDER BY id
        LIMIT $1 OFFSET $2`)
    if err != nil {
        fmt.Println("Failed to prepare statement:", err)
        return
    }
    defer stmt.Close()

    // Create channels for concurrent processing
    rowsChan := make(chan RowData, batchSize)
    doneChan := make(chan bool)
    var wg sync.WaitGroup

    // Start Excel writer goroutine
    go func() {
        currentRow := 2 // Start after header
        for rowData := range rowsChan {
            cell := fmt.Sprintf("A%d", currentRow)
            if err := streamWriter.SetRow(cell, rowData.data); err != nil {
                fmt.Printf("Error writing row %d: %v\n", currentRow, err)
            }
            currentRow++
        }
        doneChan <- true
    }()

    // Get total count with error handling
    var totalRows int
    err = db.QueryRow("SELECT COUNT(*) FROM test_table").Scan(&totalRows)
    if err != nil {
        fmt.Println("Failed to get total count:", err)
        return
    }
    fmt.Printf("Total rows to process: %d\n", totalRows)

    // Process data in concurrent batches
    const workerCount = 4
    batchChan := make(chan int, workerCount)
    processedRows := make(chan int, workerCount)
    
    // Progress tracking goroutine
    go func() {
        processed := 0
        start := time.Now()
        for count := range processedRows {
            processed += count
            elapsed := time.Since(start)
            fmt.Printf("\rProcessed %d/%d rows (%.2f%%) - Elapsed: %v", 
                      processed, totalRows, 
                      float64(processed)/float64(totalRows)*100,
                      elapsed.Round(time.Second))
        }
        fmt.Println()
    }()

    // Start worker goroutines
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    for i := 0; i < workerCount; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            localCount := 0
            
            for batchStart := range batchChan {
                rows, err := stmt.QueryContext(ctx, batchSize, batchStart)
                if err != nil {
                    fmt.Printf("Worker %d - Query failed for batch %d: %v\n", workerID, batchStart, err)
                    continue
                }

                batchCount := 0
                for rows.Next() {
                    var id int
                    var col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 string
                    if err := rows.Scan(&id, &col1, &col2, &col3, &col4, &col5, &col6, &col7, &col8, &col9, &col10); err != nil {
                        fmt.Printf("Worker %d - Error scanning row: %v\n", workerID, err)
                        continue
                    }

                    rowData := RowData{
                        data: []interface{}{id, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10},
                    }
                    rowsChan <- rowData
                    batchCount++
                    localCount++
                }

                if err := rows.Err(); err != nil {
                    fmt.Printf("Worker %d - Error during row iteration: %v\n", workerID, err)
                }
                rows.Close()
                processedRows <- batchCount
            }
            
            fmt.Printf("Worker %d completed, processed %d rows\n", workerID, localCount)
        }(i)
    }

    // Process batches
    fmt.Println("Starting batch processing...")
    batchesSubmitted := 0
    remainingRows := totalRows

    for start := 0; remainingRows > 0; start += batchSize {
        currentBatchSize := batchSize
        if remainingRows < batchSize {
            currentBatchSize = remainingRows
        }
        
        select {
        case batchChan <- start:
            batchesSubmitted++
            remainingRows -= currentBatchSize
        case <-ctx.Done():
            fmt.Println("Context cancelled, stopping batch submission")
            goto cleanup
        }
    }
    fmt.Printf("Submitted %d batches\n", batchesSubmitted)

cleanup:
    close(batchChan)

    // Wait for all workers to finish
    wg.Wait()
    close(rowsChan)
    close(processedRows)
    <-doneChan

    // Verify total rows processed
    if err := streamWriter.Flush(); err != nil {
        fmt.Println("Failed to flush stream writer:", err)
        return
    }

    fmt.Println("\nCompleted processing all rows")

    // Set column widths for better readability
    for i := range headers {
        col := string('A' + i)
        f.SetColWidth(sheetName, col, col, 15)
    }

    // Save to buffer instead of file
    buffer, err := f.WriteToBuffer()
    if err != nil {
        fmt.Println("Failed to write Excel to buffer:", err)
    }

    // Create PUT request to presigned URL
    req, err := http.NewRequest("PUT", presignedURL, bytes.NewReader(buffer.Bytes()))
    if err != nil {
        fmt.Println("Failed to create request:", err)
    }

    // Set content type for Excel file
    req.Header.Set("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    // Perform the upload
    client := &http.Client{
        Timeout: 30 * time.Minute, // Long timeout for large files
    }
    
    fmt.Println("Uploading Excel file to S3...")
    resp, err := client.Do(req)
    if err != nil {
        fmt.Println("Failed to upload file:", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        fmt.Println("Upload failed with status:", resp.Status)
    }

    fmt.Println("Export and upload completed successfully!")
}