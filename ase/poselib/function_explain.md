# 骨骼映射函数详解

## 1. _transfer_to 函数

```python
def _transfer_to(self, new_skeleton_tree: SkeletonTree):
    # 获取新骨骼树中每个关节在原始骨骼树中的索引
    old_indices = list(map(self.skeleton_tree.index, new_skeleton_tree))
    
    # 创建新的骨骼状态
    return SkeletonState.from_rotation_and_root_translation(
        new_skeleton_tree,                    # 新的骨骼树
        r=self.global_rotation[..., old_indices, :],  # 从原始骨骼中提取对应的全局旋转
        t=self.root_translation,              # 保持根节点位置不变
        is_local=False                        # 使用全局旋转表示
    )
```

### 函数作用
将骨骼状态从一个骨骼树转移到另一个骨骼树，保持动作的连续性。

### 参数说明
- `new_skeleton_tree`: 目标骨骼树，表示要转移到的骨骼结构

### 返回值
- 返回一个新的`SkeletonState`对象，包含转移后的骨骼状态

### 工作原理
1. 索引映射：
   - 使用`map`函数遍历新骨骼树中的每个关节
   - 通过`skeleton_tree.index`找到每个关节在原始骨骼树中的位置
   - 生成`old_indices`列表，记录对应关系

2. 状态转移：
   - 使用`global_rotation[..., old_indices, :]`提取对应的全局旋转
   - 保持根节点位置不变
   - 创建新的骨骼状态对象

### 使用场景
- 当需要删除或简化骨骼结构时
- 保持动作的连续性
- 适应新的骨骼拓扑结构

## 2. _remapped_to 函数

```python
def _remapped_to(self, joint_mapping: Dict[str, str], target_skeleton_tree: SkeletonTree):
    # 创建反向映射（目标关节 -> 源关节）
    joint_mapping_inv = {target: source for source, target in joint_mapping.items()}
    
    # 保留目标骨骼树中的相关关节
    reduced_target_skeleton_tree = target_skeleton_tree.keep_nodes_by_names(
        list(joint_mapping_inv)
    )
    
    # 验证关节数量一致性
    n_joints = (len(joint_mapping), len(self.skeleton_tree), len(reduced_target_skeleton_tree))
    assert len(set(n_joints)) == 1, "关节映射与骨骼树不一致"
    
    # 获取源骨骼中的关节索引
    source_indices = list(map(
        lambda x: self.skeleton_tree.index(joint_mapping_inv[x]),
        reduced_target_skeleton_tree
    ))
    
    # 提取对应的局部旋转
    target_local_rotation = self.local_rotation[..., source_indices, :]
    
    # 创建新的骨骼状态
    return SkeletonState.from_rotation_and_root_translation(
        skeleton_tree=reduced_target_skeleton_tree,  # 简化后的目标骨骼树
        r=target_local_rotation,                     # 映射后的局部旋转
        t=self.root_translation,                     # 保持根节点位置不变
        is_local=True                                # 使用局部旋转表示
    )
```

### 函数作用
根据关节映射关系，将骨骼状态重新映射到目标骨骼树。

### 参数说明
- `joint_mapping`: 源骨骼到目标骨骼的关节映射字典
- `target_skeleton_tree`: 目标骨骼树

### 返回值
- 返回一个新的`SkeletonState`对象，包含映射后的骨骼状态

### 工作原理
1. 创建反向映射：
   - 将源->目标的映射转换为目标->源的映射
   - 方便后续查找源骨骼中的对应关节

2. 简化目标骨骼树：
   - 只保留映射关系中存在的关节
   - 使用`keep_nodes_by_names`函数过滤关节

3. 验证一致性：
   - 检查关节数量是否匹配
   - 确保映射关系的完整性

4. 获取源索引：
   - 使用`map`函数遍历简化后的目标骨骼树
   - 通过反向映射找到源骨骼中的对应关节
   - 生成源关节索引列表

5. 提取旋转：
   - 从源骨骼状态中提取对应的局部旋转
   - 保持动作的语义信息

6. 创建新状态：
   - 使用简化后的目标骨骼树
   - 应用映射后的局部旋转
   - 保持根节点位置不变

### 使用场景
- 在不同骨骼结构之间建立动作对应关系
- 处理不同骨骼的关节命名差异
- 保持动作的语义信息

## 关节映射详解

### 1. 映射关系示例

假设我们有两个不同的骨骼结构：

1. 源骨骼（CMU数据库）：
```
- Hips
  - LeftUpLeg
    - LeftLeg
      - LeftFoot
  - RightUpLeg
    - RightLeg
      - RightFoot
```

2. 目标骨骼（AMP骨骼）：
```
- Pelvis
  - LeftThigh
    - LeftShin
      - LeftFoot
  - RightThigh
    - RightShin
      - RightFoot
```

### 2. 映射字典定义

对应的`joint_mapping`定义如下：
```python
joint_mapping = {
    "Hips": "Pelvis",           # 髋部对应骨盆
    "LeftUpLeg": "LeftThigh",   # 左大腿
    "LeftLeg": "LeftShin",      # 左小腿
    "LeftFoot": "LeftFoot",     # 左脚
    "RightUpLeg": "RightThigh", # 右大腿
    "RightLeg": "RightShin",    # 右小腿
    "RightFoot": "RightFoot"    # 右脚
}
```

### 3. 映射过程详解

1. 创建反向映射：
```python
joint_mapping_inv = {
    "Pelvis": "Hips",
    "LeftThigh": "LeftUpLeg",
    "LeftShin": "LeftLeg",
    "LeftFoot": "LeftFoot",
    "RightThigh": "RightUpLeg",
    "RightShin": "RightLeg",
    "RightFoot": "RightFoot"
}
```

2. 简化目标骨骼树：
```python
reduced_target_skeleton_tree = target_skeleton_tree.keep_nodes_by_names([
    "Pelvis", "LeftThigh", "LeftShin", "LeftFoot",
    "RightThigh", "RightShin", "RightFoot"
])
```

3. 获取源骨骼索引：
```python
source_indices = [
    self.skeleton_tree.index("Hips"),      # 对应Pelvis
    self.skeleton_tree.index("LeftUpLeg"), # 对应LeftThigh
    self.skeleton_tree.index("LeftLeg"),   # 对应LeftShin
    self.skeleton_tree.index("LeftFoot"),  # 对应LeftFoot
    self.skeleton_tree.index("RightUpLeg"),# 对应RightThigh
    self.skeleton_tree.index("RightLeg"),  # 对应RightShin
    self.skeleton_tree.index("RightFoot")  # 对应RightFoot
]
```

4. 应用旋转映射：
```python
target_local_rotation = self.local_rotation[..., source_indices, :]
```

### 4. 映射的目的

1. 保持动作语义：
   - 确保动作的基本特征在不同骨骼结构间保持一致
   - 例如："走路"动作在不同骨骼中都应该表现出相同的步态特征

2. 处理命名差异：
   - 不同数据库可能使用不同的命名方式
   - 通过映射关系统一不同命名系统

3. 确保动作连续性：
   - 通过局部旋转的精确映射
   - 保证动作的流畅性和自然性

### 5. 实际应用

1. 配置文件：
   - 映射关系通常存储在JSON配置文件中
   - 便于根据不同骨骼结构灵活调整

2. 映射规则：
   - 关节名称可以不同，但功能必须对应
   - 可以处理不同骨骼结构的关节数量差异
   - 支持部分关节的映射

3. 注意事项：
   - 确保映射的完整性
   - 验证关节数量的一致性
   - 检查动作的连续性

## 两个函数的区别

1. 功能侧重点：
   - `_transfer_to`: 关注骨骼结构的转换，保持全局旋转
   - `_remapped_to`: 关注关节对应关系，处理局部旋转

2. 使用顺序：
   - 通常先使用`_transfer_to`进行骨骼结构转换
   - 然后使用`_remapped_to`建立关节映射关系

3. 数据表示：
   - `_transfer_to`使用全局旋转
   - `_remapped_to`使用局部旋转

4. 应用场景：
   - `_transfer_to`适用于骨骼结构变化
   - `_remapped_to`适用于关节对应关系变化 