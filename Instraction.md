5 parameters:
1. input file -  path to file or folder with a textual file
2. type of array (instead of number of bits per counter). TO USE: byte (0 - 255), short(0 - 65 535), int(0 - 2 147 483 647)
3. number of top frequent element that we are looking for.
4. number of independent hash functions
5. count-min sketch buffer size

Example of command to launch: java main.java.com.Kandieiev.Main "input file.txt" int 20 6 2000
