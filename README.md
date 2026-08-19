# 🌐 WiFi Billing & Hotspot Management System

A web-based WiFi Billing and Hotspot Management System designed to help Internet Service Providers (ISPs), hotspot operators, apartments, hotels, cyber cafés, and other businesses manage WiFi users, packages, payments, sessions, and network access from one centralized platform.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Payment Integration](#-payment-integration)
- [MikroTik Integration](#-mikrotik-integration)
- [Security](#-security)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## 🚀 Overview

The WiFi Billing System provides a centralized dashboard for managing customers and internet services while automating the billing and access-control process. The system is designed with the needs of Kenyan and African ISPs and hotspot operators in mind, with support for flexible internet packages and payment integrations.

**Key Benefits:**
- Automate customer billing and internet access control
- Reduce manual intervention in package management
- Track revenue and customer usage in real-time
- Support multiple payment methods including M-Pesa
- Integrate seamlessly with MikroTik routers

## ✨ Key Features

### 👤 Customer Management
- Register and manage customers with detailed profiles
- View customer accounts, activity logs, and usage history
- Manage account status (active, suspended, expired)
- Bulk customer import/export functionality
- Customer search and filtering

### 📦 Internet Packages
- Create and manage unlimited WiFi packages
- Set package duration (hourly, daily, weekly, monthly)
- Configure pricing and data limits
- Create different plans for different user segments
- Package templates for quick deployment

### 💳 Billing & Payments
- Track customer payments and invoices
- Monitor payment status (pending, completed, failed)
- Automated payment reminders
- Payment history and receipts
- Support for payment gateway integration
- **M-Pesa integration** (STK Push, Paybill, Till Number)
- Multi-currency support

### 🌐 Hotspot Management
- Manage connected users in real-time
- Monitor active sessions and bandwidth usage
- Control internet access based on account/package status
- Automatic disconnection on package expiry
- Session timeout management
- MAC address binding

### 📊 Admin Dashboard
- View system statistics and analytics
- Monitor customers, payments, and revenue
- Manage packages and system settings
- Real-time network status overview
- Customizable reports and exports
- Multi-branch support (coming soon)

### 🔐 Authentication & Access Control
- Secure administrator authentication with 2FA support
- User account management with role-based permissions
- Role-based access control (Admin, Manager, Operator, Viewer)
- Session management and activity logging
- Password policies and enforcement

### 📱 Responsive Interface
- Designed for desktop, tablet, and mobile screens
- Simple, intuitive interface for administrators and customers
- Customer self-service portal
- Dark mode support
- Multi-language support (English, Swahili)

### Networking & Integrations
- MikroTik RouterOS
- Hotspot authentication
- RADIUS integration
- M-Pesa / payment gateway integration

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      Customer       │
                    │  Phone / Computer   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   WiFi / Hotspot    │
                    │      Network        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  MikroTik Router    │
                    │  / Network Device   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   WiFi Billing      │
                    │      System         │
                    │      (Django)       │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
           ┌──────────┐  ┌──────────┐  ┌──────────┐
           │ Customers│  │ Payments │  │ Packages │
           └──────────┘  └──────────┘  └──────────┘
```

## 📋 Requirements

Before installing the project, make sure you have:

- Python 3.10+
- pip
- Git
- Virtual environment support
- PostgreSQL or MySQL for production
- MikroTik RouterOS for network integration

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Briankiboi/Wifi-billing-sytem.git
cd Wifi-billing-sytem
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```
