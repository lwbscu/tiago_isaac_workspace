import os
import shutil

# 配置目标文件路径
yaml_path = '/home/ubuntu/Desktop/tiago_isaac_workspace/config/write_products.yaml'
backup_path = yaml_path + '.bak'

def modify_yaml():
    if not os.path.exists(yaml_path):
        print(f"❌ 警告: 找不到文件 {yaml_path}")
        return

    # 给原本的文件创建一个备份，绝对安全防翻车
    shutil.copy2(yaml_path, backup_path)
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    current_item_type = None
    is_modifying_scale = False
    scale_item_index = 0

    for line in lines:
        stripped = line.strip()
        
        # 1. 抓取当前节点物品的 type (探测 "- type: master_chef_can")
        if stripped.startswith('- type:'):
            current_item_type = stripped.split(':', 1)[1].strip()
            is_modifying_scale = False # 遇到新物品，重置状态
            
        # 2. 精确命中匹配项的 scale 头部
        if stripped == 'scale:' and current_item_type == 'master_chef_can':
            is_modifying_scale = True
            scale_item_index = 0
            out_lines.append(line)
            continue
            
        # 3. 如果当前处于要修改的 scale 列表中，替换为 0.8, 0.8, 1.0
        if is_modifying_scale:
            if stripped.startswith('-'):
                if scale_item_index == 0:
                    out_lines.append("  - 0.8\n")
                elif scale_item_index == 1:
                    out_lines.append("  - 1.0\n")
                elif scale_item_index == 2:
                    out_lines.append("  - 0.8\n")
                    is_modifying_scale = False # 处理完XYZ3个轴，立刻重置关闭，防止串台
                scale_item_index += 1
                continue
            else:
                # 容错：如果格式不规范，或者不是以此开头的，自动关闭替换防止误伤
                is_modifying_scale = False

        # 其他所有行一律原样保留
        out_lines.append(line)

    # 覆写回去
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

    print(f"✅ 修改成功！共精准更新了对应的 master_chef_can 大小。")
    print(f"ℹ️ 原文件已备份至: {backup_path}")

if __name__ == "__main__":
    modify_yaml()