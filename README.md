<b>License-Plate-Recognition-System</b><br>
This is a License Plate recognition System developed over Python<br><br><br>

<b>Dependencies:</b><br>
Python 3.6<br>
OpenCV<br>
numpy<br>
matplotlib<br>
pymysql<br><br>

Here I have used KNN algorithm for the classification, while the best value of K can be computedd from the output.csv file generated via running Analysis.py<br>
To train the data run Train.py and input the file name in the main method<br>
for the recognition purpose run main.<br><br>

<b>Main:</b><br>
In the case of an ivalid plate occuring in the image press the keyboard key (->) to train the chracters of the plate<br>
Press (ESC) to exit<br>
after the plate has been recognised correctly, if you're a registered user simply input fine else register yourself<br>
you can also register yourself via the plates.db file<br>
the .db file contains a database with two tables, fine and plates, enter your details in the later<br><br>

<b>Analysis:</b><br>
this gives an idea of amount of actual error caused while the recognition process<br>
Enter the original license plate number and select the plate by pressing any key on the keyboard when popup image appears<br>
In the case of an ivalid plate occuring in the image press the keyboard key (->)<br>
Press (ESC) to exit<br><br>

<b>Train:</b><br>
Enter the charters one by one when when highlighted within the image<br>
the characters are mapped with the images and the numpy array is stored in float32 formatin the txt files classifications and flattened_images needed for the recognition process<br>
In the case of an ivalid charcter occuring in the image press the keyboard key (->)<br>
Press (ESC) to exit<br><br>

<b>Import:</b><br>
loads allthe images in a particular folder to train<br>

<b>Chars:</b><br>
Identifies all the characters in the image<br><br>

<b>Plates:</b><br>
Collectively identifies plate in image based on the output of the chars file<br><br>

<b>Preprocess:</b><br>
cleans the image in a better grayscale form for improvised output<br><br>

<b>Links used for references:<b><br>
<a href= "http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_tutorials.html"> Open Cv Tutorials </a><br>
<a href= "http://codereview.stackexchange.com/questions/tagged/python">Python Syntaxes and Querries</a><br>
<a href= "http://scikit-learn.org/stable/">Machine learning algorithms</a><br>
<a href= "https://docs.python.org/3/">Python Documentation for functions</a><br>
