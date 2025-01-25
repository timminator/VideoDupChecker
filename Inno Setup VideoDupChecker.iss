#define MyAppName "VideoDupChecker"
#define MyAppVersion "1.1.0"
#define MyAppURL "https://github.com/timminator/VideoDupChecker"
#define MyAppExeName "VideoDupChecker.exe"
#define MyInstallerVersion "1.0.0.0"
#define MyAppCopyright "timminator"

#include "environment.iss"

[Setup]
SignTool=signtool $f
AppId={{..}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyInstallerVersion}
AppCopyright={#MyAppCopyright}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={commonpf64}\{#MyAppName}
UsePreviousAppDir=yes
LicenseFile=..\LICENSE
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputBaseFilename={#MyAppName}-v{#MyAppVersion}-setup-x64
SetupIconFile=..\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=classic
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}"; Permissions: everyone-full

[Files]
Source: "..\VideoDupChecker\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\_bz2.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\_decimal.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\_hashlib.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\_lzma.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\_wmi.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\libcrypto-3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\python312.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\select.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\vcruntime140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\VideoDupChecker\vcruntime140_1.dll"; DestDir: "{app}"; Flags: ignoreversion

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
    if (CurStep = ssPostInstall) and WizardIsTaskSelected('envPath')
    then EnvAddPath(ExpandConstant('{app}'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
    if CurUninstallStep = usPostUninstall
    then EnvRemovePath(ExpandConstant('{app}'));
end;

[Tasks]
Name: envPath; Description: "Add to PATH variable"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"