# same as above but powershell instead of bash
echo "WARNING: This will delete all dot files, ~ files, gcode, .swp, .png, .stl and .scad files for ALL SUBPROJECTS."
# get the answer
$REPLY = Read-Host -Prompt "Are you sure you want to continue?
(y/n)"
  if($REPLY -eq "y"){
    echo "Deleting all dot files, .swp .png .stl and .scad files for ALL PROJECTS.."
    rm  */.*
    rm */*.scad
    rm */*.stl
    rm */*.png
    rm */*.swp
    rm */*.gcode

    echo "Done."
}
# now else
else{
  echo "Exiting without changing files.."
}