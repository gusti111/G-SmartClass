
param([string]$Root="G-SmartClass")
$ErrorActionPreference="Stop"
function New-Folder($p){ if(!(Test-Path $p)){ New-Item -ItemType Directory -Path $p | Out-Null } }
function New-File($p){
  $dir=Split-Path $p
  if($dir){ New-Folder $dir }
  if(!(Test-Path $p)){ New-Item -ItemType File -Path $p | Out-Null }
}
New-Folder $Root
Set-Location $Root

$features=@(
"authentication/login","authentication/register","authentication/forgot_password","authentication/email_verification","authentication/pair_device",
"dashboard","academic/courses","academic/materials","academic/assignments","academic/quizzes","academic/gradebook","academic/attendance","academic/certificates",
"library","community","chat","meeting","calendar","notification","analytics","profile","settings","admin",
"ai/tutor","ai/quiz_generator","ai/summary","ai/flashcard","ai/translator","ai/study_plan"
)

$base=@(
".github/workflows",".vscode",
"docs/Architecture","docs/Database","docs/API","docs/UI-UX","docs/ERD","docs/Roadmap",
"assets/logo","assets/icon","assets/fonts","assets/illustration","assets/lottie","assets/splash",
"desktop/config","desktop/core","desktop/routes","desktop/cache","desktop/logger","desktop/middleware","desktop/resources/icons","desktop/resources/images","desktop/themes","desktop/tests/unit","desktop/tests/integration",
"web/public","web/src/components","web/src/pages","web/src/services","web/src/assets","web/src/utils",
"mobile/lib","mobile/assets","mobile/test","backend/functions/src","firebase","shared/constants","shared/models","shared/theme","scripts","tools"
)
$base|%{New-Folder $_}

foreach($f in $features){
  foreach($s in @("ui","assets","styles","controllers","models","repositories","services","widgets","views")){
    New-Folder ("desktop/features/{0}/{1}" -f $f,$s)
  }
  $leaf=Split-Path $f -Leaf
  New-File ("desktop/features/{0}/ui/{1}.ui" -f $f,$leaf)
  New-File ("desktop/features/{0}/styles/{1}.qss" -f $f,$leaf)
  New-File ("desktop/features/{0}/views/{1}_view.py" -f $f,$leaf)
  New-File ("desktop/features/{0}/controllers/{1}_controller.py" -f $f,$leaf)
  New-File ("desktop/features/{0}/models/{1}_model.py" -f $f,$leaf)
  New-File ("desktop/features/{0}/repositories/{1}_repository.py" -f $f,$leaf)
  New-File ("desktop/features/{0}/services/{1}_service.py" -f $f,$leaf)
}

$coreFiles=@(
"desktop/app.py","desktop/config/firebase.py","desktop/config/settings.py","desktop/routes/router.py",
"desktop/middleware/auth_guard.py","desktop/logger/logger.py",
"web/index.html","mobile/lib/main.dart","backend/functions/src/index.ts",
"firebase/firestore.rules","firebase/storage.rules","firebase/database.rules.json","README.md",".gitignore"
)
$coreFiles|%{New-File $_}
Write-Host "G-SmartClass structure generated successfully."
