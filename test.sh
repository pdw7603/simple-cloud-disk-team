#!/bin/bash
set -e
SERVER_IP="192.168.41.130"
SERVER_PORT="8081"
TEST_USERNAME="test_team_user"
TEST_PASSWORD="123456"
echo -e "\033[32m==============================================\033[0m"
echo -e "\033[32m          简易云盘项目自动化测试开始           \033[0m"
echo -e "\033[32m==============================================\033[0m"
echo -e "\n\033[33m【测试1】服务状态检测\033[0m"
if netstat -tulpn | grep -q ":${SERVER_PORT}"; then
    echo -e "\033[32m服务启动正常\033[0m"
else
    echo -e "\033[31m服务未启动，终止测试\033[0m" && exit 1
fi
echo -e "\n\033[33m【测试2】注册接口验证\033[0m"
REGISTER_RESULT=$(curl -s -X POST -d "username=${TEST_USERNAME}&password=${TEST_PASSWORD}&repassword=${TEST_PASSWORD}" http://${SERVER_IP}:${SERVER_PORT}/register)
echo ${REGISTER_RESULT} | grep -q "注册成功" && echo -e "\033[32m注册接口通过\033[0m" || echo -e "\033[31m注册接口失败\033[0m"
echo -e "\n\033[33m【测试3】登录接口验证\033[0m"
LOGIN_RESULT=$(curl -s -c - -X POST -d "username=${TEST_USERNAME}&password=${TEST_PASSWORD}" http://${SERVER_IP}:${SERVER_PORT}/login)
echo ${LOGIN_RESULT} | grep -q "session" && echo -e "\033[32m登录接口通过\033[0m" || echo -e "\033[31m登录接口失败\033[0m"
echo -e "\n\033[32m==============================================\033[0m"
echo -e "\033[32m          简易云盘项目自动化测试结束           \033[0m"
echo -e "\033[32m==============================================\033[0m"
