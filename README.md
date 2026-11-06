# csg_draw: 一个用于绘制csg模型剖面图的程序

## 环境配置

推荐使用 uv + `.venv`。`.venv` 使用 uv 管理的 CPython 3.13，不跟随 Arch 的系统 Python 更新；依赖版本由 `pyproject.toml` 和 `uv.lock` 固定。

首次配置：

```bash
uv sync
```

`uv sync` 会安装运行依赖 `numpy`，以及开发依赖 `pytest`、`ruff`。

日常使用：

```bash
source .venv/bin/activate
make run
```

也可以直接运行：

```bash
.venv/bin/python -m examples.basic
```

常用命令：

```bash
make run     # 运行基础 Cell 示例
make demo     # 生成 output/slice_z.png 和 output/slice_plane.png
make example  # 运行完整示例 examples/shielded.py
make conflict # 运行冲突几何示例 examples/conflict.py
make test     # 运行 pytest
make lint    # 运行 ruff check
make format  # 运行 ruff format
```

如果 `.venv` 已存在且需要重建，可以加 `--clear`：

```bash
uv venv --python 3.13 --managed-python --seed --clear .venv
uv sync
```

`.venv` 当前验证版本：Python 3.13.18，numpy 2.4.4。

提交时建议把 `pyproject.toml`、`uv.lock` 和 `.python-version` 一起纳入版本控制，以固定 Python 和依赖版本。

## 目录结构

```text
shapes.py                 基本曲面
macro.py                  macrobody
cell.py                   Cell + 内部表达式树
geometry.py               Geometry + 重叠报告
slicing.py                平面采样
render.py                 二维渲染
transforms.py             刚体变换
_geom_syntax_core.py      语法解析共享核心
mcnp_geom_syntax.py       MCNP 方言
phits_geom_syntax.py      PHITS 方言
set_syntax.py             PHITS set: 变量
geom_syntax.py            通用加载/识别接口
cell_syntax.py            旧接口兼容层

examples/                 示例脚本
tests/                    测试
docs/                     参考手册
```

## 几何约定

- 使用右手笛卡尔坐标系。
- `Shape.is_positive()` 返回点是否位于曲面的严格正侧。
- 对于封闭曲面，正侧就是外部。
- 正好位于曲面上的点不属于正侧，归入负侧；因此：
  - `-surface` 定义的 cell 包含边界；
  - `+surface` 定义的 cell 不包含边界。
- `Cell` 使用 `SignedShape` 的正负号表示 MCNP 的正负侧。

## Cell 表达式

`Cell` 对应 MCNP/PHITS 的 cell card，内部持有一个 CSG 表达式树：

```text
Cell
  └── expression
        ├── SurfaceTerm
        ├── Intersection
        ├── Union
        ├── Complement
        └── CellReference
```

- 现有 `Cell([-OSphere(1), +Plane(...)])` 仍然表示交集，保持兼容；
- 表达式树节点和 `Cell` 一起位于 `cell.py`；
- `Cell` 是唯一的公开体元对象；
- `CellReference` 用于 `#cell_id` 补集，需要由 `Geometry` 提供求值上下文；
- 循环 cell 引用会抛出 `ValueError`。

## MCNP/PHITS 几何语法

几何语法相关模块：

```text
_geom_syntax_core.py     私有共享核心
mcnp_geom_syntax.py      MCNP surface/cell/input
phits_geom_syntax.py     PHITS surface/cell/input
geom_syntax.py           通用识别与加载接口
cell_syntax.py           旧接口兼容层
```

### 解析单个 cell card

```python
from mcnp_geom_syntax import parse_mcnp_cell
from shapes import OSphere, Plane

surfaces = {
    1: OSphere(1),
    2: Plane(1, 0, 0, 0),
    3: OSphere(2),
}

parsed = parse_mcnp_cell(
    "10 1 -1.0 -1 2 -3 imp:n=1",
    surfaces,
)
cell = parsed.to_cell()
```

### 解析 surface card

```python
from mcnp_geom_syntax import parse_mcnp_surface

surface = parse_mcnp_surface("1 SO 2")
# surface.surface_id == 1
# surface.shape 是 OSphere(2)
# surface.transform 是可选的 TR 编号
```

支持：

```text
P, PX, PY, PZ
SO, S, SX, SY, SZ
C/X, C/Y, C/Z, CX, CY, CZ
K/X, K/Y, K/Z, KX, KY, KZ
SQ, GQ
TX, TY, TZ
RPP, RCC, BOX, HEX/RHP, REC
TRC, ELL, WED, ARB, SPH
```

### 加载完整输入

自动识别 MCNP/PHITS：

```python
from geom_syntax import load_geometry

model = load_geometry("model.inp")
# model.syntax
# model.title
# model.surfaces
# model.cells
# model.geometry

labels = model.geometry.sample(grid.x, grid.y, grid.z)
```

也可以显式指定：

```python
from geom_syntax import parse_geometry

mcnp_model = parse_geometry(text, syntax="mcnp")
phits_model = parse_geometry(text, syntax="phits")
```

支持的几何语法：

- 带符号 surface ID：`-1`、`+2`、`3`；
- 隐式交集：`-1 2 -3`；
- 并集：`-1 : -2`；
- 补集：`#5`、`#(-1 2)`；
- 括号；
- cell card 前缀：cell ID、material、density；
- 尾部参数保留在 `ParsedCell.options`；
- `$` 行内注释；
- MCNP 的 title / cell / surface 分块；
- PHITS 的 `[Cell]` / `[Surface]` section。

当前未处理：

- `u=` / `lat=` / `fill=` 会被明确拒绝，等待 universe/lattice 支持；
- macrobody facet 引用（如 `1.2`）暂不支持；
- ARB 当前按凸多面体处理，且暂不支持多行 ARB；
- material/tally 等数据卡。

当前支持 `LIKE n BUT` 的基础形式，例如：

```text
3 LIKE 2 BUT TRCL=1 MAT=2 RHO=2.5
```

`cell_syntax.py` 保留为兼容层，旧代码仍然可以：

```python
from cell_syntax import parse_mcnp_cell, parse_phits_cell
```

## TR 变换

`transforms.py` 提供刚体变换：

```text
p_global = R · p_local + t
p_local  = Rᵀ · (p_global - t)
```

几何采样使用逆变换：先把全局采样点变回曲面/ cell 的局部坐标，再调用原始 `is_positive`。因此球、圆柱、圆锥、torus 和 macrobody 都不需要重写方程。

支持的 PHITS `[Transform]`：

- `tr1`：角度使用 radian；
- `*tr1`：角度使用 degree；
- `M = ±1`：直接给出旋转矩阵；
- `M = ±2`：按 z、y、x 顺序旋转；
- `M = ±3`：指定旋转中心、轴顺序和角度。

示例：

```text
[Transform]
tr1 10 0 0 1 0 0 0 1 0 0 0 1 1

[Surface]
1 1 SO 2
```

这表示把球心平移到 `(10, 0, 0)`。

MCNP 的 `TRn` 数据卡也支持：

```text
TR1 10 0 0 1 0 0 0 1 0 0 0 1
```

Surface card 的 transform number 和 cell 的 `trcl=...` 都会应用到对应几何。`LoadedModel` 提供：

```python
model.transforms
model.cells[i].transform_id
```

PHITS cell 也支持内联 `trcl`：

```text
1 0 -1 trcl=(0 0 20)
1 0 -1 trcl=(10 0 0 1 0 0 0 1 0 0 0 1)
1 0 -1 *trcl=(0 0 0 90 0 0 0 0 0 0 0 0 2)
```

- 3 个值：纯平移；
- 12 个值：按 `M=1` 处理；
- 13 个值：最后一个值为 `M`；
- `*trcl` 使用 degree，普通 `trcl` 使用 radian。

内联变换只保存在 `ParsedCell.inline_transform` / `Cell.transform`，不会进入 `LoadedModel.transforms`。

当前限制：

- 内联 `trcl` 只支持括号形式，暂不支持裸写多行；
- MCNP cell 暂只支持 `trcl=number`；
- 尚未实现 lattice/fill 的变换组合；
- macrobody facet 引用暂不支持。

## PHITS `set:` 表达式

`set_syntax.py` 支持识别 PHITS 用户变量，并翻译为 Python 表达式：

```text
set: c1[ 52.3 ] c2[ 2 * pi ] c3[ c1 * 1.e-8 ]
```

会被翻译为类似：

```python
c1 = 52.3
c2 = 2 * math.pi
c3 = c1 * 1.e-8
```

`load_phits_text` 会先执行所有 `set:` 定义，并在后续输入行中替换 `cN` 变量，然后再解析 surface、cell 和 transform。

加载后的模型提供：

```python
model.set_variables     # {"c1": 52.3, ...}
model.set_statements    # ("c1 = 52.3", ...)
```

当前支持：

- `c1`～`c999` 数值变量；
- `pi`；
- `sin/cos/tan/asin/acos/atan/atan2`；
- `sinh/cosh/tanh`；
- `exp/log/log10/sqrt`；
- `floor/ceil/fabs`；
- `abs/min/max/pow`；
- Fortran `D` 指数，例如 `1.0D-3`；
- `^` 作为幂运算；
- `$`、`#`、`!` 行内注释。

当前不支持：

- `set:` 字符变量 `%name%[...]`；
- 跳过 section 中的 `set:` 语义；
- `infl:` 文件插入；
- `set:` 多行续写。

当前未进行 Git 提交。

## 多 cell 与切面采样

`geometry.Geometry` 按顺序保存多个 cell，采用 first-match 语义；`slicing.make_slice_grid` 可以在任意 `Plane` 上生成二维采样网格。

```python
from cell import Cell
from geometry import CellEntry, Geometry
from shapes import OSphere, Plane
from slicing import make_slice_grid

space = Geometry([
    CellEntry(Cell([-OSphere(1)]), cell_id=1, material=1, color="tab:red"),
    CellEntry(
        Cell([-OSphere(2), +OSphere(1)]),
        cell_id=2,
        material=2,
        color="tab:blue",
    ),
])

grid = make_slice_grid(
    Plane(0, 0, 1, 0),
    u_range=(-3.0, 3.0),
    v_range=(-3.0, 3.0),
    nx=600,
    ny=600,
)

labels = space.sample(grid.x, grid.y, grid.z)
# labels 为 (600, 600) 的 cell 索引数组，-1 表示背景

# 需要检测重叠时：
conflict_labels = space.sample(grid.x, grid.y, grid.z, mark_conflicts=True)
# 多个 cell 同时命中的点返回 geometry.MULTI_DEFINED（-2）
```

## 切面图渲染

`render.render_slice` 可以把采样结果绘制成彩色切面图，`render.save_slice` 会直接保存图片。

```bash
make demo
```

会生成：

```text
output/slice_z.png
output/slice_plane.png
```

也可以在自己的脚本中调用：

```python
from render import save_slice

save_slice(space, grid, "output/slice.png")
```

默认按 cell ID 着色；也可以按 material 着色：

```python
save_slice(
    space,
    grid,
    "output/slice_material.png",
    color_by="material",
    void_color="#d9d9d9",
)
```

- `color_by="cell"`：按 `CellEntry.color` 或 cell ID；
- `color_by="material"`：相同 material 使用相同颜色；
- `material == 0` 使用 `void_color`；
- 图例按 material 去重；
- `CellEntry.density` 会保留从输入文件解析出的密度。

## 综合示例

`examples/shielded.py` 构造一个更完整的 CSG 模型：

- cell 1：半径 1 的内球；
- cell 2：半径 1 到 2 的球壳；
- cell 3：长方体内部、球壳外部的填充区域；
- 其余区域为背景。

运行：

```bash
make example
```

会先输出四个采样检查点，再生成：

```text
output/example_z.png
output/example_x.png
output/example_plane.png
```

## 冲突几何示例

`examples/conflict.py` 演示三种冲突情况：

1. 三个球体互相重叠，按 `Geometry` 中 cell 的顺序采用 first-match；
2. 同一个 cell 同时使用 `-OSphere(1)` 和 `+OSphere(1)`，得到一个空 cell；
3. 两个 cell 使用相同 `cell_id`，`Geometry` 会直接拒绝。

运行：

```bash
make conflict
```

示例会输出每个采样点被哪些 cell 命中，以及网格中重叠区域的数量。

重叠检测会生成警告文件：

```text
output/conflict_overlap_warning.csv
```

CSV 包含重叠点的物理坐标、命中数量和对应的 cell ID：

```text
x,y,z,claim_count,cell_ids
...
```

也可以在自己的脚本中调用：

```python
from geometry import write_overlap_report

report = write_overlap_report(
    space,
    grid.x,
    grid.y,
    grid.z,
    "output/overlap_warning.csv",
)
print(report.count, report.max_claim_count)
```

渲染时重叠区域使用洋红色标记为 `ID=Multi-Defined`，右侧图例会列出所有 cell ID 和 `ID=Multi-Defined`。

最终生成：

```text
output/conflict_z.png
```

## 功能和进度

- [ ] 审阅此前的python代码;
- [ ] 设计兼容 MCNP, PHITS 等主流 CSG 建模主导的粒子输运蒙特卡洛计算的 SURFACE 曲面和宏曲面卡严格的数学类定义.(以手动编程定义了所有曲面和大部分宏曲面的python类/子类);
- [ ] 设计任意切面(尽量保证切面使用之前定义的平面类)的切面图, 并对含有CSG元素的格点进行涂色;
- [ ] \(如果上一条无法满足\)设计平行于xOy, xOz, yOz的平面的切面图, 并对含有CSG元素的格点进行涂色;
- [ ] 设计一套自动识别 MCNP 语法的程序使其可以根据提供的 MCNP 输入文件绘制切面图;
- [ ] 设计一套自动识别 PHITS 语法的程序使其可以根据提供的 PHITS 输入文件绘制切面图;
