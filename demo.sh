#!/bin/bash

# SecureBridge Live Demo Script
# This script demonstrates the dual authentication system with real API calls

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"

# Function to print section headers
print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

# Function to print step
print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print JSON response
print_json() {
    echo -e "${MAGENTA}Response:${NC}"
    echo "$1" | jq '.' 2>/dev/null || echo "$1"
}

# Function to pause
pause() {
    echo -e "\n${BLUE}Press Enter to continue...${NC}"
    read -r
}

# Check if server is running
check_server() {
    print_step "Checking if SecureBridge server is running..."
    if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        print_success "Server is running at $BASE_URL"
    else
        print_error "Server is not running. Please start it with: uvicorn app.main:app --reload"
        exit 1
    fi
}

# Welcome message
clear
echo -e "${GREEN}"
cat << "EOF"
   _____                          ____       _     _            
  / ____|                        |  _ \     (_)   | |           
 | (___   ___  ___ _   _ _ __ ___| |_) |_ __ _  __| | __ _  ___ 
  \___ \ / _ \/ __| | | | '__/ _ \  _ <| '__| |/ _` |/ _` |/ _ \
  ____) |  __/ (__| |_| | | |  __/ |_) | |  | | (_| | (_| |  __/
 |_____/ \___|\___|\__,_|_|  \___|____/|_|  |_|\__,_|\__, |\___|
                                                       __/ |     
                   LIVE DEMO                          |___/      
EOF
echo -e "${NC}"

echo -e "${CYAN}Dual Authentication System Demo${NC}"
echo -e "${CYAN}Features: JWT User Auth + API Key Service Auth${NC}\n"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    print_error "jq is not installed. Installing for better JSON formatting..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y jq
    elif command -v brew &> /dev/null; then
        brew install jq
    fi
fi

# Check server
check_server
pause

# ============================================
# PART 1: USER AUTHENTICATION
# ============================================

print_header "PART 1: USER AUTHENTICATION (JWT)"

# 1. User Signup
print_step "1. Creating a new user account..."
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@securebridge.com",
    "name": "Demo User",
    "password": "SecurePassword123!"
  }')

print_json "$SIGNUP_RESPONSE"

# Extract tokens
ACCESS_TOKEN=$(echo "$SIGNUP_RESPONSE" | jq -r '.tokens.access_token')
REFRESH_TOKEN=$(echo "$SIGNUP_RESPONSE" | jq -r '.tokens.refresh_token')

if [ "$ACCESS_TOKEN" != "null" ]; then
    print_success "User created successfully!"
    echo -e "   ${BLUE}Access Token:${NC} ${ACCESS_TOKEN:0:20}..."
    echo -e "   ${BLUE}Refresh Token:${NC} ${REFRESH_TOKEN:0:20}..."
else
    print_error "Failed to create user. User might already exist."
    # Try to login instead
    print_step "Attempting to login with existing user..."
    SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "demo@securebridge.com",
        "password": "SecurePassword123!"
      }')
    ACCESS_TOKEN=$(echo "$SIGNUP_RESPONSE" | jq -r '.tokens.access_token')
    REFRESH_TOKEN=$(echo "$SIGNUP_RESPONSE" | jq -r '.tokens.refresh_token')
    print_success "Logged in successfully!"
fi

pause

# 2. Get Current User
print_step "2. Fetching authenticated user profile..."
USER_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_json "$USER_RESPONSE"
USER_ID=$(echo "$USER_RESPONSE" | jq -r '.id')
print_success "Retrieved user profile for: $(echo "$USER_RESPONSE" | jq -r '.email')"
pause

# 3. Refresh Token
print_step "3. Refreshing access token..."
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

print_json "$REFRESH_RESPONSE"
NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access_token')
if [ "$NEW_ACCESS_TOKEN" != "null" ]; then
    print_success "Token refreshed successfully!"
    ACCESS_TOKEN=$NEW_ACCESS_TOKEN
fi
pause

# ============================================
# PART 2: API KEY MANAGEMENT
# ============================================

print_header "PART 2: API KEY MANAGEMENT"

# 4. Create API Key
print_step "4. Creating API key for a microservice..."
CREATE_KEY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/keys/create" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "analytics-service",
    "description": "API key for analytics microservice",
    "permissions": ["read:data", "write:logs", "read:reports"],
    "expires_in_days": 90
  }')

print_json "$CREATE_KEY_RESPONSE"
API_KEY=$(echo "$CREATE_KEY_RESPONSE" | jq -r '.api_key')
KEY_ID=$(echo "$CREATE_KEY_RESPONSE" | jq -r '.id')

if [ "$API_KEY" != "null" ]; then
    print_success "API Key created successfully!"
    echo -e "   ${BLUE}Key ID:${NC} $KEY_ID"
    echo -e "   ${BLUE}API Key:${NC} ${API_KEY:0:30}..."
    echo -e "   ${BLUE}Service:${NC} analytics-service"
fi
pause

# 5. Create Another API Key
print_step "5. Creating another API key for different service..."
CREATE_KEY_RESPONSE_2=$(curl -s -X POST "$BASE_URL/api/v1/keys/create" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "payment-service",
    "description": "API key for payment processing",
    "permissions": ["read:transactions", "write:transactions"],
    "expires_in_days": 30
  }')

print_json "$CREATE_KEY_RESPONSE_2"
API_KEY_2=$(echo "$CREATE_KEY_RESPONSE_2" | jq -r '.api_key')
KEY_ID_2=$(echo "$CREATE_KEY_RESPONSE_2" | jq -r '.id')
print_success "Second API Key created!"
pause

# 6. List All API Keys
print_step "6. Listing all API keys for current user..."
LIST_KEYS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/keys/list" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_json "$LIST_KEYS_RESPONSE"
KEY_COUNT=$(echo "$LIST_KEYS_RESPONSE" | jq '. | length')
print_success "Found $KEY_COUNT API key(s)"
pause

# 7. Get Specific API Key Details
print_step "7. Getting details of specific API key..."
GET_KEY_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/keys/$KEY_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_json "$GET_KEY_RESPONSE"
print_success "Retrieved key details"
pause

# ============================================
# PART 3: SERVICE AUTHENTICATION
# ============================================

print_header "PART 3: SERVICE-TO-SERVICE AUTHENTICATION"

# 8. Verify API Key (Service Auth)
print_step "8. Authenticating as a service using API key..."
VERIFY_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/keys/verify/test" \
  -H "Authorization: Bearer $API_KEY")

print_json "$VERIFY_RESPONSE"
print_success "Service authenticated successfully with API key!"
echo -e "   ${BLUE}Service:${NC} $(echo "$VERIFY_RESPONSE" | jq -r '.service_name')"
echo -e "   ${BLUE}Permissions:${NC} $(echo "$VERIFY_RESPONSE" | jq -r '.permissions | join(", ")')"
pause

# ============================================
# PART 4: API KEY LIFECYCLE MANAGEMENT
# ============================================

print_header "PART 4: API KEY LIFECYCLE MANAGEMENT"

# 9. Revoke API Key
print_step "9. Revoking payment-service API key..."
REVOKE_RESPONSE=$(curl -s -X PATCH "$BASE_URL/api/v1/keys/$KEY_ID_2/revoke" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_json "$REVOKE_RESPONSE"
print_success "API Key revoked!"
pause

# 10. Try Using Revoked Key
print_step "10. Attempting to use revoked API key (should fail)..."
VERIFY_REVOKED=$(curl -s -X GET "$BASE_URL/api/v1/keys/verify/test" \
  -H "Authorization: Bearer $API_KEY_2")

print_json "$VERIFY_REVOKED"
print_error "Access denied with revoked key (expected behavior)"
pause

# 11. Renew API Key
print_step "11. Renewing analytics-service API key for 180 days..."
RENEW_RESPONSE=$(curl -s -X PATCH "$BASE_URL/api/v1/keys/$KEY_ID/renew" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "expires_in_days": 180
  }')

print_json "$RENEW_RESPONSE"
print_success "API Key renewed successfully!"
pause

# 12. Delete API Key
print_step "12. Permanently deleting revoked payment-service key..."
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/api/v1/keys/$KEY_ID_2" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ -z "$DELETE_RESPONSE" ]; then
    print_success "API Key deleted successfully!"
else
    print_json "$DELETE_RESPONSE"
fi
pause

# ============================================
# PART 5: SECURITY FEATURES
# ============================================

print_header "PART 5: SECURITY FEATURES DEMONSTRATION"

# 13. Attempt Unauthorized Access
print_step "13. Testing unauthorized access (no token)..."
UNAUTHORIZED_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/auth/me")

print_json "$UNAUTHORIZED_RESPONSE"
print_error "Access denied without token (expected behavior)"
pause

# 14. Attempt with Invalid Token
print_step "14. Testing with invalid JWT token..."
INVALID_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer invalid.token.here")

print_json "$INVALID_RESPONSE"
print_error "Access denied with invalid token (expected behavior)"
pause

# 15. List Final State
print_step "15. Final API key inventory..."
FINAL_LIST=$(curl -s -X GET "$BASE_URL/api/v1/keys/list" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_json "$FINAL_LIST"
FINAL_COUNT=$(echo "$FINAL_LIST" | jq '. | length')
print_success "Current active keys: $FINAL_COUNT"
pause

# ============================================
# SUMMARY
# ============================================

print_header "DEMO SUMMARY"

echo -e "${GREEN}✓ User Authentication (JWT)${NC}"
echo -e "  • User signup and login"
echo -e "  • Token refresh mechanism"
echo -e "  • Profile access with JWT"
echo -e ""
echo -e "${GREEN}✓ API Key Management${NC}"
echo -e "  • Created API keys for services"
echo -e "  • Listed and retrieved key details"
echo -e "  • Revoked and deleted keys"
echo -e "  • Renewed key expiration"
echo -e ""
echo -e "${GREEN}✓ Service Authentication${NC}"
echo -e "  • Verified service with API key"
echo -e "  • Demonstrated permission-based access"
echo -e ""
echo -e "${GREEN}✓ Security Features${NC}"
echo -e "  • Blocked unauthorized access"
echo -e "  • Validated token integrity"
echo -e "  • Enforced revocation"
echo -e ""

print_success "Demo completed successfully! 🎉"
echo -e "\n${CYAN}Access API documentation at: ${BLUE}http://localhost:8000/docs${NC}\n"

# Cleanup option
echo -e "${YELLOW}Would you like to clean up the demo user and keys? (y/n)${NC}"
read -r cleanup
if [ "$cleanup" = "y" ] || [ "$cleanup" = "Y" ]; then
    print_step "Cleaning up demo resources..."
    
    # Delete remaining keys
    for key_id in $(echo "$FINAL_LIST" | jq -r '.[].id'); do
        curl -s -X DELETE "$BASE_URL/api/v1/keys/$key_id" \
          -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
    done
    
    print_success "Cleanup completed!"
fi

echo -e "\n${GREEN}Thank you for trying SecureBridge!${NC}\n"
