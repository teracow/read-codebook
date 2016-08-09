![icon](images/icon.png) read-codebook.py
---
This is a **[python](https://en.wikipedia.org/wiki/Python_(programming_language))** script to read through a previously decrypted **[Codebook](https://www.zetetic.net/codebook/)** database file. The idea is to quickly traverse the dB structure to get to the required infomation. This is all console based and is very simple to use. No modifications to the database are possible.

---
###**Description:**

1. The user supplies a plaintext SQLite database file created in **[Codebook](https://www.zetetic.net/codebook/)**. 

2. Then select the category, then finally the entry. 

---
###**Usage:**

    $ ./read-codebook.py [PARAMETERS] ...

Allowable parameters are indicated with a hyphen then a single character or the alternative form with 2 hypens and the full-text. Single character parameters (without arguments) can be concatenated. e.g. `-cdeghkqsv`. Parameters can be specified as follows:  


***Required***

`-i` or `--input-file [FILENAME]`  
The plaintext database file to read. 

---
###**Development Environment:**

- [openSUSE](https://www.opensuse.org/) - *13.2 64b*
- GNU BASH - *v4.2.53*
- Geany - *v1.24.1*
- KDE Development Platform - *v4.14.9*
- QT - *v4.8.6*
- SQLCipher - *v3.8.10.2* 
- SQLite - *v3.8.6*
- [pudn](http://en.pudn.com/downloads151/sourcecode/graph/detail656399_en.html) - script icon


Suggestions / comments / bug reports / advice (are|is) most welcome. :) [email me](mailto:teracow@gmail.com)

---
###**Known Issues:**

- (2016-08-09) - None.

---
###**Work-in-Progress:**

- (2016-08-09) - Lots! New project so many things to do! ![smiley](images/smiley.png)
 
---
###**To-Do List:**

- (2016-08-09) - option to save selected entry to text file.
- (2016-08-09) - need to loop back after checking out selected entry.
- (2016-08-09) - perform decryption on original strip.db file.
