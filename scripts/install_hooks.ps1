# Installs the committed pre-commit secret scan into this clone's .git/hooks.
$root = git rev-parse --show-toplevel
Copy-Item "$root/scripts/hooks/pre-commit" "$root/.git/hooks/pre-commit" -Force
Write-Output "installed .git/hooks/pre-commit"