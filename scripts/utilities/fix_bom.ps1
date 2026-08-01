$bytes = [System.IO.File]::ReadAllBytes('D:\Portable_Soft\hermes\launch.bat')
Write-Host "First 3 bytes: $($bytes[0]) $($bytes[1]) $($bytes[2])"
Write-Host "Size: $($bytes.Length)"
# If BOM (EF BB BF), remove it
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    $noBom = $bytes[3..($bytes.Length-1)]
    [System.IO.File]::WriteAllBytes('D:\Portable_Soft\hermes\launch.bat', $noBom)
    Write-Host "BOM removed!"
} else {
    Write-Host "No BOM found"
}
