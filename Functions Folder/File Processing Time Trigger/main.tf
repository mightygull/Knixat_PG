data "azurerm_resource_group" "main" {
  name = var.mainRG
}

resource "azurerm_service_plan" "dis" {
  name                = var.serviceP
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "Y1"
}

resource "azurerm_linux_function_app" "first" {
  name                = var.funcApp
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location

  storage_account_name       = azurerm_storage_account.primary.name
  storage_account_access_key = azurerm_storage_account.primary.primary_access_key
  service_plan_id            = azurerm_service_plan.dis.id

  site_config {}
}

resource "azurerm_logic_app_workflow" "notif" {
  name                = var.logicapp
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
}

resource "azurerm_storage_account" "primary" {
  name                     = var.storageACC
  resource_group_name      = data.azurerm_resource_group.main.name
  location                 = data.azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "source" {
  name                  = var.sourName
  storage_account_name  = azurerm_storage_account.primary.name
  container_access_type = var.contAType
}

resource "azurerm_storage_container" "destination" {
  name                  = var.destName
  storage_account_name  = azurerm_storage_account.primary.name
  container_access_type = var.contAType
}
