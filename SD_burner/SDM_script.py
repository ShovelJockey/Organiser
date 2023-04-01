from subprocess import run
import sys


def sdm_customise_image(cscript_path: str, wpa_config_path: str, timezone: str, wifi_country: str, user_name: str, image_path: str) -> None:
    '''
    Makes edits to raspi image, these edits will be applied to all SD's flashed from this image.

    Parameters:
    wpa_config_path, str : path to wpa settings file
    timezone, str : code for timezone for raspi i.e. 'Europe/London'
    wifi_country, str : country code for location of wifi network
    user_name, str : user name for all raspi on this system
    image_path, str : path to image to customise
    '''
    shell_command = f'''sudo /usr/local/sdm/sdm --customize
                                                --cscript {cscript_path}
                                                --wpa {wpa_config_path} 
                                                --timezone {timezone} 
                                                --wifi-country {wifi_country} 
                                                --user {user_name} 
                                                --password-user placeholder 
                                                --svcdisable userconfig
                                                --autologin 
                                                --batch 
                                                --restart 
                                                {image_path}'''

    shell_command = " ".join(line.strip() for line in shell_command.splitlines())

    run(shell_command, shell=True, text=True, check=True, stderr=sys.stderr, stdout=sys.stdout)


def sdm_burn_image(sd_path: str, dhcp_path: str, hostname: str, password: str, image_path: str) -> None:
    '''
    Burns the image to SD card setting a defined hostname, password for user and the settings from the dhcpcd config.

    Parameters:
    sd_path, str : /dev/ disk id for SD card
    dhcp_path, str : path to dhcp settings for setting static IP during burn
    hostname, str : unique hostname for pi
    password, str : new password for default user added to image during customisation
    image_path, str : path to image to burn SD's from
    '''
    shell_command = f'''sudo /usr/local/sdm/sdm --burn 
                                                /dev/{sd_path} 
                                                --dhcpcd {dhcp_path} 
                                                --hostname {hostname}
                                                --password-user {password}
                                                --expand-root 
                                                {image_path}'''

    shell_command = " ".join(line.strip() for line in shell_command.splitlines())

    run(shell_command, shell=True, text=True, check=True, stderr=sys.stderr, stdout=sys.stdout)


def sdm_extend_image(image_path: str) -> None:
    '''
    Extends the image to ensure enough space for additional packages/files.

    Parameters:
    image_path, str : path to image to extend
    '''
    run(f'sudo /usr/local/sdm/sdm --extend --xmb 1536 {image_path}',
                shell=True, text=True, check=True, stderr=sys.stderr, stdout=sys.stdout)
