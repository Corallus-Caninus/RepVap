#RENDER:
cd Inlet_Flange 
powershell -command "& python3 Inlet_Flange.py"
cd .. 
cd Nozzle_Array
powershell -command "& python3 Nozzle_Array.py"
cd ..
cd Reservoir
powershell -command "& python3 Bottle_Stand.py"
cd ..
cd Spill_Guard
powershell -command "& python3 Spill_Guard.py"
cd ..
cd Tube_Linkage
powershell -command "& python3 Tube_Linkage.py"
cd ..
cd Water_Bracket
powershell -command "& python3 Water_Bracket.py"
cd ..
