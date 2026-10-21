param([string]$type, [string]$keys, [int]$wait = 2, [string]$shot = "shot")
# Помощник для управления VM TempleOS2026: ввод текста/клавиш и скриншот.
$vb = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$vm = "TempleOS2026"
$codes = @{ enter = "1c 9c"; esc = "01 81"; space = "39 b9"; y = "15 95"; n = "31 b1"; tab = "0f 8f"; up = "e0 48 e0 c8"; down = "e0 50 e0 d0"; left = "e0 4b e0 cb"; right = "e0 4d e0 cd"; bksp = "0e 8e"; f5 = "3f bf"; shiftesc = "2a 01 81 aa" }
if ($type) { & $vb controlvm $vm keyboardputstring $type.Replace('"','\"') }
if ($keys) {
    foreach ($k in $keys.Split(",")) { & $vb controlvm $vm keyboardputscancode ($codes[$k].Split(" ")); Start-Sleep -Milliseconds 300 }
}
Start-Sleep $wait
& $vb controlvm $vm screenshotpng "C:\Users\slaye\TempleOS2026\shots\$shot.png"
