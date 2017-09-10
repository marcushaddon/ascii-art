# Changelog

## 0.1

## 0.2

1. Output sequences are now PNGs with transparent backgrounds.
2. --help messages added.
3. 'Reduce Flicker' function works. NOTE: reducing flicker will also inherently reduce the variety of characters from which it can choose. ANOTHER NOTE: Cranking the reduce flicker up to something like 127 (roughly half of 255, meaning pixels are basically either considered black or white) can have some neat effects.
4. Characters list can be edited without error.
5. You SHOULDN'T need to run ulimit -n abignumber anymore?
6. Characters list is stored in external 'chars.txt' file. The first line is prepended by a '#',
and is only there to serve as a reference when creating new character sets. To create a new character set,
copy this line without the '#' (NOTE: the line begins with a space) and paste it below, removing/adding whatever you want. You can store multiple character sets by prepending sets you dont want to currently use with a '#'. The program will use the first character set it finds without a '#' at the beginning.
7. A new optional argument '--outfile' has been added. By default, the program will create a folder named like <INFILE NAME> + '_out', and will overwrite this folder each time the given infile is processed. If you want to process the same file multiple times, you can specify --outfile <DESCRIPTIVE FILE NAME>.
8. All arguments (except for --infile and --outfile) have defaults specified in ascii/settings.py. You can edit these so you dont have to specify them manually each time. You can also override select settings by specifying their argument in the command line.
