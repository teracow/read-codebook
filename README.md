![icon](images/icon.png) read-codebook.py
---
This is a combination of **[BASH](https://en.wikipedia.org/wiki/Bash_\(Unix_shell\))** and **[Python](https://en.wikipedia.org/wiki/Python_(programming_language))** scripts to decrypt and read through a **[Codebook](https://www.zetetic.net/codebook/)** database '**strip.db**' file. The idea is to quickly traverse the dB structure to get to required infomation. This is entirely console based and is easy to use. No modifications to the database are possible.

---
###**Description:**

1. Ensure your SQLite database file created in **[Codebook](https://www.zetetic.net/codebook/)** ('**strip.db**') is available locally. 

2. Run `./decrypt-strip.sh -i strip.db`

3. Enter the matching **[Codebook](https://www.zetetic.net/codebook/)** passphrase for '**strip.db**'.

3. A decrypted (plaintext) database is then written to '**/dev/shm/decrypt-strip/plaintext.db**'.

4. Then open this plaintext dB using the included Python reader to examine the contents. There is an option to write particular entries to text files in the working directory.

5. When you're done, quit the reader and delete the plaintext database file.

---
###**Notes:**

As this compromises the security of the original database, it is recommended that this only be done in a secure environment (i.e. don't run this on Windows) and only if you understand why. I do not take any responsibilty for the integrity and security of your data. 

These script were written for my convenience so that I can access the '**strip.db**' file in the event that my iPhone is lost, stolen or damaged. Being able to do so means I'm more likely to store important information in my copy of the great **[Codebook](https://www.zetetic.net/codebook/)** app. ![smiley](images/smiley.png)

At this time, I've decided not to use pysqlcipher to reduce the dependance on other packages.

---
###**Usage:**

    $ ./decrypt-strip.sh -i [PATHFILE to strip.db]

or, if the database file has already been decrypted:

    $ ./read-codebook.py -i [PATHFILE to plaintext.db]

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
