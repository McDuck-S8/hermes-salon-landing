$src = 'D:\Portable_Soft\hermes\launch.bat'
$bytes = [System.IO.File]::ReadAllBytes($src)
# Detect OEM codepage (866 for Russian Windows)
$oemCodePage = [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.OEMCodePage
$oemEncoding = [System.Text.Encoding]::GetEncoding($oemCodePage)
# Read as UTF-8 first
$utf8 = [System.Text.Encoding]::UTF8
$text = $utf8.GetString($bytes)
# Write back in OEM encoding (no BOM)
$noBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($src, $text, $oemEncoding)
Write-Host "Saved in OEM codepage $oemCodePage"
