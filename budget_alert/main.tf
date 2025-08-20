terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80.0"
    }
  }

  required_version = ">= 1.3.0"
}
provider "azurerm" {
  features {}
skip_provider_registration = true
}

# Create Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# Create Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${var.resource_group_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

# Create Subnet
resource "azurerm_subnet" "main" {
  name                 = "default"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create VMSS
resource "azurerm_linux_virtual_machine_scale_set" "main" {
  name                = var.vmss_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard_DS1_v2"
  instances           = 2
  admin_username      = "azureuser"
  admin_password      = "P@ssword1234!"  # Use Key Vault or secure way in production
  disable_password_authentication = false

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  upgrade_mode = "Manual"

  network_interface {
    name    = "vmss-nic"
    primary = true

    ip_configuration {
      name      = "internal"
      subnet_id = azurerm_subnet.main.id
    }
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}

# Create Budget Alert for the Resource Group
resource "azurerm_consumption_budget_resource_group" "budget" {
  name               = var.budget_name
  resource_group_id  = azurerm_resource_group.main.id  
  amount             = var.budget_amount
  time_grain         = "Monthly"

  time_period {
    start_date = "2025-08-20T00:00:00Z"
  end_date   = "2050-12-31T00:00:00Z"
  }

  notification {
    enabled         = true
    operator        = "GreaterThan"
    threshold       = 80.0
    threshold_type  = "Actual"
    contact_emails  = [var.email_address]
  }

  notification {
    enabled         = true
    operator        = "GreaterThan"
    threshold       = 100.0
    threshold_type  = "Actual"
    contact_emails  = [var.email_address]
  }
}
