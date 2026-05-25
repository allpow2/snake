# Snack — Python 项目编码规范

本文件为 AI 辅助开发提供项目级编码规范，所有代码生成必须遵循。

## 语言与环境
- Python 3.10+，使用类型注解
- 依赖管理：所有依赖列于 `requirements.txt`
- 仅使用标准库 + Pygame，不引入其他第三方库

## 项目结构约定
- 按功能模块拆分：`config.py` `snake.py` `food.py` `score.py` `game.py` `renderer.py` `main.py`
- 每个模块只暴露必要的公开接口，内部实现用 `_` 前缀标记
- `main.py` 仅负责初始化和事件循环，不含游戏逻辑
- `game.py` 负责状态机、碰撞检测、计时器、特殊机制

## 命名规范
- 类名：`PascalCase`，函数/方法：`snake_case`，常量：`UPPER_SNAKE_CASE`
- 私有属性/方法：`_leading_underscore`
- 布尔变量：`is_` / `has_` 前缀（如 `is_paused`, `has_eaten`, `boost_active`）
- 属性暴露布尔状态用 `@property`，如 `should_quit` `boost_active` `golden_active`

## 代码风格
- 遵循 PEP 8，缩进 4 空格，每行不超过 100 字符
- import 顺序：标准库 → 第三方库 → 本地模块，各组之间空一行
- 不写 docstring 和注释，除非代码行为需要解释 WHY

## 类型注解
- 所有公开方法标注参数类型和返回值类型
- 使用 Python 3.10+ 原生语法：`list[X]`、`X | None`
- 元组坐标统一格式：`tuple[int, int]`

## 游戏架构约定

### 状态管理
- 游戏状态使用 `enum.Enum`（`GameState`），不散落字符串常量
- 状态转换集中在 `Game` 类，禁止跨模块修改状态
- 每个状态只响应对应按键子集

### 数据与渲染分离
- 实体类（Snake、Food、GoldenFood）只包含数据和行为，不导入 pygame
- 所有 `pygame.draw.*` / `pygame.Surface.*` 调用集中在 `renderer.py`
- 配置值集中在 `config.py`，运行时不可修改
- 渲染器通过读取 Game 实例获取状态，不修改游戏数据

### 坐标系统
- 游戏逻辑使用网格坐标 `(col, row)`，范围 `[0, COLS) x [0, ROWS)`
- 渲染器负责网格坐标 → 像素坐标转换：`pixel = grid * CELL_SIZE`
- 平滑移动通过插值实现：`interp` 参数（0~1）传入渲染器

### 输入处理
- 按键映射定义在 `config.py`，使用 `pygame.K_*` 常量
- 方向变更必须防反向：调用 `DIRECTION_OPPOSITES` 判断
- **中文输入法兼容**：
  - `main.py` 启动时调用 `pygame.key.stop_text_input()`
  - `game.py` 同时提供 `handle_input(event)` 和 `handle_held_keys(keys)` 双通道
  - `handle_held_keys` 使用 `pygame.key.get_pressed()` 作为 IME 兜底

### 金色食物系统
- `GoldenFood` 独立实体类，`active` 属性控制显示
- 出现条件：计时器 >= 随机间隔 且 非 boost 状态 且 当前无金色食物
- 出现时普通食物隐藏（renderer 跳过绘制），同一时间只有一种食物
- 吃到后：加分 + 启动 boost（速度×2 + 成长×2，持续 10s）+ 重置计时器
- 计时器在 boost 期间暂停，boost 结束后重新累积
- 间隔随机范围配置在 `config.py`：`GOLDEN_FOOD_MIN_INTERVAL` ~ `GOLDEN_FOOD_MAX_INTERVAL`

### 粒子系统
- `Particle` 使用 `@dataclass` 定义轻量数据结构
- 粒子在 `game.py` 中创建和管理，在 `renderer.py` 中绘制
- 吃食物时触发：`_emit_particles()` 以食物位置为中心圆形扩散
- 生命周期以游戏 tick 递减，结束后自动移除

### 性能与动画
- 渲染 60 FPS（`clock.tick(60)`），逻辑 tick 速率 = `game.speed` Hz
- tick 累积器模式解耦渲染和逻辑：`while accumulator >= interval: update()`
- 蛇身颜色使用线性插值渐变（head 最亮 → tail 最暗）
- boost 期间蛇身使用高亮配色，眼睛瞳孔变红
- 金色食物使用 sin 脉冲动画（光晕大小 + 透明度），星形旋转

## 错误处理
- 不写 try-except 处理不会发生的异常
- 文件 I/O（最高分读写）仅需最简 try-except
- 不使用断言做参数校验

## 安全
- 最高分文件使用 `os.path.expanduser("~")` 绝对路径
- 不使用 `eval()` / `exec()` / `pickle` 加载外部数据
