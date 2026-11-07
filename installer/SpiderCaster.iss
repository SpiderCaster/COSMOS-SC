; SpiderCaster user installer. No admin. The shortcut runs the studio.
; Build from engine\:  ISCC installer\SpiderCaster.iss
; Requires dist\SpiderCaster.exe from:  py -3.14 -m PyInstaller SpiderCaster.spec

#define AppVersion "0.1.0"

[Setup]
AppId={{A7C3E1B4-6D20-4F8A-9C55-0B2E7D4A91F6}
AppName=SpiderCaster
AppVersion={#AppVersion}
AppPublisher=SpiderCaster
DefaultDirName={localappdata}\SpiderCaster
DefaultGroupName=SpiderCaster
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=SpiderCaster-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\SpiderCaster.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "..\dist\SpiderCaster.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\SpiderCaster"; Filename: "{app}\SpiderCaster.exe"; Parameters: "start"; WorkingDir: "{app}"; Comment: "Open the SpiderCaster studio"
Name: "{autodesktop}\SpiderCaster"; Filename: "{app}\SpiderCaster.exe"; Parameters: "start"; WorkingDir: "{app}"; Comment: "Open the SpiderCaster studio"

[Run]
Filename: "{app}\SpiderCaster.exe"; Parameters: "start"; WorkingDir: "{app}"; Description: "Open the SpiderCaster studio"; Flags: postinstall nowait skipifsilent
