variable "location" {
  description = "Azure region for all resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "vmss_name" {
  description = "Name of the VMSS"
  type        = string
}

variable "budget_name" {
  description = "Name of the budget alert"
  type        = string
}

variable "budget_amount" {
  description = "Monthly budget amount in USD"
  type        = number
}

variable "email_address" {
  description = "Email address to receive budget alert notifications"
  type        = string
}

