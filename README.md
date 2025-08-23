# Classroom-Person-Segregation-Model
This is a model which takes an images and segregates the people
<br>
First download python
<br>
Next in terminal run
<br>
pip install -r .\requirements.txt
<br>
Run the code on your pc as local host with any port number <br>
Open Powershell <br>
go to the directory of your image using "cd" command <br>
Type <br>
curl -X POST -F "file=@image_1.jpg" http://localhost:8000/detect_students/
<br>
If you are using powershell type curl.exe instead of curl