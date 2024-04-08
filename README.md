# Outline VPN Automatic IP Rotation

Rotates the public IP address of an Azure VM. We use this to rotate the public IP address of a VM that is used as an Outline VPN server. This allows the VPN to evade blocking, since Outline is already difficult to block on-the-fly and often must be blocked manually by IP address.

This script supports Azure and Porkbun DNS, but can be easily adapted to at least work with other DNS providers. It's designed to be run as a cron job.

## Setup
- Set up your .env file, as described in the `.env.example` file.
- `pip3 install -r requirements.txt`
- Set up in crontab, like this: `0 0 * * * cd /home/username/azure-porkbun-ip-rotation && python3 main.py`