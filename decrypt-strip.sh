#!/bin/bash

# decrypt-strip.sh

# Copyright (C) 2016 Teracow Software

# If you find this code useful, please let me know. :) teracow@gmail.com

# Decrypt 'strip.db' with a supplied password and write to 'plaintext.db'

script_details="decrypt-strip.sh (2016-08-11)"
encrypted_pathfile="strip.db"
unencrypted_pathfile="plaintext.db"
decrypter="sqlcipher"
reader="read-codebook.py"
reader_pathfile="$(dirname "$BASH_SOURCE")/${reader}"

echo "$script_details"

if [ ! -e "$encrypted_pathfile" ] ; then
	echo "! Encrypted database file not found: [$encrypted_pathfile]"
	exit
fi

if [  -e "$unencrypted_pathfile" ] ; then
	echo "! Plaintext database file already exists: [$unencrypted_pathfile]"
	exit
fi

which "$decrypter" > /dev/null 2>&1

if [ "$?" -ne "0" ] ; then
	echo " ! $decrypter is unavailable."
	exit
fi

echo -n "? Enter your CodeBook passphrase: "
read -r passphrase

sql_cmd="PRAGMA key = '$passphrase'; ATTACH DATABASE '$unencrypted_pathfile' AS plaintext KEY ''; SELECT sqlcipher_export('plaintext'); DETACH DATABASE plaintext;"

echo -n "- Decrypting database ... "

echo "$sql_cmd" | "$decrypter" "$encrypted_pathfile" > /dev/null 2>&1

if [ "$?" -eq "0" ] ; then
	echo "done!"

	echo -n "? Open in [$reader] ? "
	read -n 1 result
	echo

	if [ "$result" == "y" ] || [ "$result" == "Y"  ] ; then
		"$reader_pathfile" -i "$unencrypted_pathfile"
		echo -n "? Delete [$unencrypted_pathfile] ? "
		read -n 1 result
		echo

		if [ "$result" == "y" ] || [ "$result" == "Y"  ] ; then
			rm -f "$unencrypted_pathfile"
		fi
	fi
else
	echo "failed!"
	rm -f "$unencrypted_pathfile"
fi
