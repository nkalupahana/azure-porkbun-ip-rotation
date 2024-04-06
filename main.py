import os
import requests
import time

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import PublicIPAddress, IPAllocationMethod, PublicIPAddressSku
from dotenv import load_dotenv

load_dotenv(".env")

credential = DefaultAzureCredential()
network_client = NetworkManagementClient(credential, os.environ["AZURE_SUBSCRIPTION_ID"])
interface = network_client.network_interfaces.get(os.environ["AZURE_RG_NAME"], os.environ["AZURE_NI_NAME"])
old_ip = interface.ip_configurations[0].public_ip_address

print("Creating new IP...")
new_ip_attr = PublicIPAddress(
    location=os.environ["AZURE_LOCATION"],
    sku=PublicIPAddressSku(name="Standard"),
    public_ip_allocation_method=IPAllocationMethod.static
)
new_ip = network_client.public_ip_addresses.begin_create_or_update(os.environ["AZURE_RG_NAME"], f"vpn-rotated-ip-{time.time()}", new_ip_attr).result()

print("Associating new IP...")
interface.ip_configurations[0].public_ip_address = new_ip
network_client.network_interfaces.begin_create_or_update(os.environ["AZURE_RG_NAME"], os.environ["AZURE_NI_NAME"], interface)
time.sleep(30)

print("Deleting old IP...")
network_client.public_ip_addresses.begin_delete(os.environ["AZURE_RG_NAME"], old_ip.id.split("/")[-1]).result()

print(f"New IP: {new_ip.ip_address}")

print("Updating DNS...")
resp = requests.post(f"https://porkbun.com/api/json/v3/dns/editByNameType/{os.environ['PORKBUN_DOMAIN_NAME']}/A/{os.environ['PORKBUN_SUBDOMAIN_NAME']}", json={
    "apikey": os.environ["PORKBUN_API_PK"],
    "secretapikey": os.environ["PORKBUN_API_SK"],
    "content": new_ip.ip_address
})

print("Done!")