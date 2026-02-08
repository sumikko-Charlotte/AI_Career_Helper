#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯云数据库实例外网端口查询脚本
支持查询 MySQL 和 CynosDB (TDSQL-C) 实例的外网端口
"""

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

# 导入 MySQL 和 CynosDB SDK
from tencentcloud.cdb.v20170320 import cdb_client, models as cdb_models
from tencentcloud.cynosdb.v20190107 import cynosdb_client, models as cynosdb_models

# ==========================================
# 配置区域：请替换为你的腾讯云 API 密钥
# ==========================================
SECRET_ID = "你的SecretId"  # 替换为你的 SecretId
SECRET_KEY = "你的SecretKey"  # 替换为你的 SecretKey

# 腾讯云所有地域列表
REGIONS = [
    "ap-beijing",      # 北京
    "ap-shanghai",     # 上海
    "ap-guangzhou",    # 广州
    "ap-chengdu",      # 成都
    "ap-chongqing",    # 重庆
    "ap-shenzhen-fsi", # 深圳金融
    "ap-shanghai-fsi", # 上海金融
    "ap-beijing-fsi", # 北京金融
    "ap-hongkong",     # 香港
    "ap-singapore",    # 新加坡
    "ap-mumbai",       # 孟买
    "ap-seoul",        # 首尔
    "ap-bangkok",      # 曼谷
    "ap-tokyo",        # 东京
    "na-siliconvalley", # 硅谷
    "na-ashburn",      # 弗吉尼亚
    "na-toronto",      # 多伦多
    "sa-saopaulo",     # 圣保罗
    "eu-frankfurt",    # 法兰克福
    "eu-moscow",       # 莫斯科
]


def get_mysql_instances(cred, region):
    """查询指定地域的 MySQL 实例"""
    try:
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdb.tencentcloudapi.com"
        
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        client = cdb_client.CdbClient(cred, region, clientProfile)
        
        req = cdb_models.DescribeDBInstancesRequest()
        req.Limit = 100  # 每页最多100个实例
        
        resp = client.DescribeDBInstances(req)
        
        instances = []
        if resp.Items:
            for item in resp.Items:
                # 获取外网地址和端口
                instance_info = {
                    "InstanceId": item.InstanceId,
                    "InstanceName": item.InstanceName,
                    "Status": item.Status,
                    "EngineVersion": item.EngineVersion,
                    "Vip": item.Vip,  # 内网地址
                    "Vport": item.Vport,  # 内网端口
                    "WanDomain": item.WanDomain if hasattr(item, 'WanDomain') else None,  # 外网域名
                    "WanPort": item.WanPort if hasattr(item, 'WanPort') else None,  # 外网端口
                    "WanStatus": item.WanStatus if hasattr(item, 'WanStatus') else None,  # 外网状态
                    "WanVip": item.WanVip if hasattr(item, 'WanVip') else None,  # 外网IP
                }
                instances.append(instance_info)
        
        return instances
    except TencentCloudSDKException as e:
        if "InvalidParameter" in str(e) or "AuthFailure" in str(e):
            raise
        # 某些地域可能没有实例，返回空列表
        return []
    except Exception as e:
        print(f"  ⚠️  查询 MySQL 实例时出错: {e}")
        return []


def get_cynosdb_instances(cred, region):
    """查询指定地域的 CynosDB (TDSQL-C) 实例"""
    try:
        httpProfile = HttpProfile()
        httpProfile.endpoint = "cynosdb.tencentcloudapi.com"
        
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        client = cynosdb_client.CynosdbClient(cred, region, clientProfile)
        
        req = cynosdb_models.DescribeClustersRequest()
        req.Limit = 100
        
        resp = client.DescribeClusters(req)
        
        instances = []
        if resp.DBInstances:
            for item in resp.DBInstances:
                # 获取外网地址和端口
                instance_info = {
                    "ClusterId": item.ClusterId,
                    "ClusterName": item.ClusterName,
                    "Status": item.Status,
                    "DbVersion": item.DbVersion if hasattr(item, 'DbVersion') else None,
                    "VpcId": item.VpcId if hasattr(item, 'VpcId') else None,
                    "SubnetId": item.SubnetId if hasattr(item, 'SubnetId') else None,
                }
                
                # 查询实例的网络信息（外网地址和端口）
                try:
                    detail_req = cynosdb_models.DescribeClusterDetailRequest()
                    detail_req.ClusterId = item.ClusterId
                    detail_resp = client.DescribeClusterDetail(detail_req)
                    
                    if detail_resp.Detail:
                        detail = detail_resp.Detail
                        instance_info["WanDomain"] = detail.WanDomain if hasattr(detail, 'WanDomain') else None
                        instance_info["WanPort"] = detail.WanPort if hasattr(detail, 'WanPort') else None
                        instance_info["WanStatus"] = detail.WanStatus if hasattr(detail, 'WanStatus') else None
                        instance_info["WanVip"] = detail.WanVip if hasattr(detail, 'WanVip') else None
                        instance_info["Vip"] = detail.Vip if hasattr(detail, 'Vip') else None
                        instance_info["Vport"] = detail.Vport if hasattr(detail, 'Vport') else None
                except Exception as e:
                    print(f"    ⚠️  查询实例详情时出错: {e}")
                
                instances.append(instance_info)
        
        return instances
    except TencentCloudSDKException as e:
        if "InvalidParameter" in str(e) or "AuthFailure" in str(e):
            raise
        # 某些地域可能没有实例，返回空列表
        return []
    except Exception as e:
        print(f"  ⚠️  查询 CynosDB 实例时出错: {e}")
        return []


def format_region_name(region):
    """格式化地域名称"""
    region_map = {
        "ap-beijing": "北京",
        "ap-shanghai": "上海",
        "ap-guangzhou": "广州",
        "ap-chengdu": "成都",
        "ap-chongqing": "重庆",
        "ap-hongkong": "香港",
        "ap-singapore": "新加坡",
        "ap-mumbai": "孟买",
        "ap-seoul": "首尔",
        "ap-bangkok": "曼谷",
        "ap-tokyo": "东京",
        "na-siliconvalley": "硅谷",
        "na-ashburn": "弗吉尼亚",
        "na-toronto": "多伦多",
        "sa-saopaulo": "圣保罗",
        "eu-frankfurt": "法兰克福",
        "eu-moscow": "莫斯科",
    }
    return region_map.get(region, region)


def main():
    """主函数"""
    print("=" * 80)
    print("腾讯云数据库实例外网端口查询工具")
    print("=" * 80)
    print()
    
    # 检查密钥配置
    if SECRET_ID == "你的SecretId" or SECRET_KEY == "你的SecretKey":
        print("❌ 错误：请先配置 SECRET_ID 和 SECRET_KEY")
        print("   在脚本中替换第 20-21 行的密钥配置")
        return
    
    # 创建凭证
    try:
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
    except Exception as e:
        print(f"❌ 创建凭证失败: {e}")
        return
    
    all_instances = []
    
    # 遍历所有地域
    print("正在查询所有地域的数据库实例...")
    print()
    
    for region in REGIONS:
        region_name = format_region_name(region)
        print(f"📍 查询地域: {region_name} ({region})")
        
        # 查询 MySQL 实例
        mysql_instances = get_mysql_instances(cred, region)
        if mysql_instances:
            print(f"  ✅ 找到 {len(mysql_instances)} 个 MySQL 实例")
            for inst in mysql_instances:
                inst["Type"] = "MySQL"
                inst["Region"] = region
                inst["RegionName"] = region_name
                all_instances.append(inst)
        
        # 查询 CynosDB 实例
        cynosdb_instances = get_cynosdb_instances(cred, region)
        if cynosdb_instances:
            print(f"  ✅ 找到 {len(cynosdb_instances)} 个 CynosDB 实例")
            for inst in cynosdb_instances:
                inst["Type"] = "CynosDB"
                inst["Region"] = region
                inst["RegionName"] = region_name
                all_instances.append(inst)
        
        if not mysql_instances and not cynosdb_instances:
            print(f"  ⚪ 该地域无实例")
        
        print()
    
    # 输出结果
    print("=" * 80)
    print("查询结果汇总")
    print("=" * 80)
    print()
    
    if not all_instances:
        print("⚠️  未找到任何数据库实例")
        print()
        print("可能的原因：")
        print("1. API 密钥配置错误")
        print("2. API 密钥权限不足")
        print("3. 账号下确实没有数据库实例")
        return
    
    print(f"共找到 {len(all_instances)} 个数据库实例")
    print()
    
    # 按地域分组输出
    regions_with_instances = {}
    for inst in all_instances:
        region = inst["RegionName"]
        if region not in regions_with_instances:
            regions_with_instances[region] = []
        regions_with_instances[region].append(inst)
    
    for region_name, instances in regions_with_instances.items():
        print(f"【{region_name}】")
        print("-" * 80)
        
        for idx, inst in enumerate(instances, 1):
            instance_id = inst.get("InstanceId") or inst.get("ClusterId", "N/A")
            instance_name = inst.get("InstanceName") or inst.get("ClusterName", "N/A")
            db_type = inst.get("Type", "N/A")
            
            # 外网信息
            wan_domain = inst.get("WanDomain") or inst.get("WanVip") or "未开启外网"
            wan_port = inst.get("WanPort") or "N/A"
            wan_status = inst.get("WanStatus")
            
            # 内网信息
            vip = inst.get("Vip") or "N/A"
            vport = inst.get("Vport") or "N/A"
            
            print(f"  {idx}. {instance_name} ({instance_id})")
            print(f"     类型: {db_type}")
            print(f"     状态: {inst.get('Status', 'N/A')}")
            
            if wan_status == 1 or wan_status == "1":
                print(f"     ✅ 外网已开启")
                print(f"     外网地址: {wan_domain}")
                print(f"     外网端口: {wan_port}")
            else:
                print(f"     ⚠️  外网未开启")
                print(f"     外网地址: {wan_domain}")
                print(f"     外网端口: {wan_port}")
            
            print(f"     内网地址: {vip}")
            print(f"     内网端口: {vport}")
            print()
        
        print()
    
    # 输出 JSON 格式（可选）
    print("=" * 80)
    print("JSON 格式输出（用于脚本处理）")
    print("=" * 80)
    print(json.dumps(all_instances, indent=2, ensure_ascii=False))
    print()
    
    # 输出建议
    print("=" * 80)
    print("排查建议")
    print("=" * 80)
    print()
    print("如果外网端口显示为 N/A 或未开启，请检查：")
    print("1. 在腾讯云控制台 → 数据库实例 → 连接信息中查看外网端口")
    print("2. 确认外网访问是否已开启")
    print("3. 检查安全组是否开放了外网端口")
    print("4. 检查数据库实例的网络配置")
    print()


if __name__ == "__main__":
    try:
        main()
    except TencentCloudSDKException as e:
        print(f"❌ 腾讯云 SDK 错误: {e}")
        print()
        print("可能的原因：")
        print("1. API 密钥配置错误")
        print("2. API 密钥权限不足（需要云数据库相关权限）")
        print("3. 网络连接问题")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
