#!/bin/bash

# decrypt-strip.sh

# Copyright (C) 2016 Teracow Software

# If you find this code useful, please let me know. :) teracow@gmail.com

# Decrypt 'strip.db' with a supplied password and write to 'plaintext.db'

# $1 = pathfile to 'strip.db'

Init()
	{

	local script_file="decrypt-strip.sh"
	local script_name="${script_file%.*}"
	script_details="${script_file} (2016-08-12)"

	temp_path="/dev/shm/${script_name}"
	local encrypted_file="strip.db"
	local unencrypted_file="plaintext.db"
	decrypter="sqlcipher"
	reader="read-codebook.py"
	unencrypted_pathfile="${temp_path}/${unencrypted_file}"
	reader_pathfile="$(dirname "$BASH_SOURCE")/${reader}"
	encrypted_pathfile="./${encrypted_file}"

	echo "$script_details"
	echo

	}

WhatAreMyOptions()
	{

	# if getopt exited with an error then show help to user
	[ "$user_parameters_result" != "0" ] && echo && show_help_only=true && return 2

	eval set -- "$user_parameters"

	while true ; do
		case "$1" in
			-i | --input-file )
				encrypted_pathfile="$2"
				shift 2		# shift to next parameter in $1
				;;
			-- )
				shift		# shift to next parameter in $1
				break
				;;
			* )
				break		# there are no more matching parameters
				;;
		esac
	done

	}

# check for command-line parameters
user_parameters=$(getopt -o i: --long input-file: -n $(readlink -f -- "$0") -- "$@")
user_parameters_result=$?
user_parameters_raw="$@"

Init
WhatAreMyOptions

which "$decrypter" > /dev/null 2>&1

if [ "$?" -ne "0" ] ; then
	echo " ! $decrypter is unavailable."
	exit
fi

if [ ! -e "$encrypted_pathfile" ] ; then
	echo "! Encrypted database file not found: [$encrypted_pathfile]"

	exit 1
fi

mkdir -p "$temp_path"

if [ "$?" -gt "0" ] ; then
	echo "! Unable to create a temporary directory! Exiting."
	exit 1
fi

if [ -e "$unencrypted_pathfile" ] ; then
	echo "! Plaintext database file already exists: [$unencrypted_pathfile]"
	echo -n "? Delete this file first? (y/n) "
	read -n 1 result
	echo

	if [ "$result" == "y" ] || [ "$result" == "Y" ] ; then
		rm -f "$unencrypted_pathfile"
	else
		exit 1
	fi
fi

echo -n "? Enter your CodeBook passphrase: "

# http://stackoverflow.com/questions/4316730/linux-scripting-hiding-user-input-on-terminal
while IFS= read -r -s -n1 pass; do
	if [[ -z $pass ]]; then
		echo
		break
	else
		echo -n '*'
		passphrase+=$pass
	fi
done

sql_cmd="PRAGMA key = '$passphrase'; ATTACH DATABASE '$unencrypted_pathfile' AS plaintext KEY ''; SELECT sqlcipher_export('plaintext'); DETACH DATABASE plaintext;"

echo -n "- Decrypting database ... "

echo "$sql_cmd" | "$decrypter" "$encrypted_pathfile" > /dev/null 2>&1

if [ "$?" -eq "0" ] ; then
	echo "done!"

	echo -n "? Open file in [$reader] ? (y/n) "
	read -n 1 result
	echo

	if [ "$result" == "y" ] || [ "$result" == "Y" ] ; then
		"$reader_pathfile" -i "$unencrypted_pathfile"
		echo -n "? Delete file [$unencrypted_pathfile] ? (y/n) "
		read -n 1 result
		echo

		if [ "$result" == "y" ] || [ "$result" == "Y" ] ; then
			rm -f "$unencrypted_pathfile"
		fi
	fi
else
	echo "failed!"
	rm -f "$unencrypted_pathfile"
fi
