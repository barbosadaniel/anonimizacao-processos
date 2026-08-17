# Script para testar upload do PDF
$uri = 'http://127.0.0.1:8000/process-file'
$filePath = 'exemplos\processo_teste_anonimizacao.pdf'

Write-Host "Iniciando upload..."
$start = Get-Date

try {
    Add-Type -AssemblyName System.Net.Http
    $client = New-Object System.Net.Http.HttpClient
    $fileContent = New-Object System.Net.Http.ByteArrayContent([System.IO.File]::ReadAllBytes($filePath))
    $fileContent.Headers.ContentType = "application/pdf"
    
    $content = New-Object System.Net.Http.MultipartFormDataContent
    $content.Add($fileContent, "file", [System.IO.Path]::GetFileName($filePath))
    
    $response = $client.PostAsync($uri, $content).Result
    $responseBody = $response.Content.ReadAsStringAsync().Result
    
    $elapsed = ((Get-Date) - $start).TotalSeconds
    Write-Host "Tempo: ${elapsed}s"
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Response:"
    $responseBody | ConvertFrom-Json | ConvertTo-Json -Depth 5
} catch {
    Write-Error "Erro: $_"
}
