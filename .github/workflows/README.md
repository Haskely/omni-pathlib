# 使用教程

## Publish to PyPI

### 1. 在 PyPI 和 TestPyPI 上创建带有可信发布者的项目

> https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/

需要在两个平台上分别进行配置：
1. TestPyPI: https://test.pypi.org/
2. PyPI: https://pypi.org/

在每个平台上执行以下步骤：
1. 注册并登录
2. 打开 manage/account/publishing/ 页面
3. 找到 Add a new pending publisher
4. 填写以下信息：
   - PyPI Project Name：本例为 `omni_pathlib`
   - Owner：本例为 `Haskely`
   - Repository name：本例为 `omni-pathlib`
   - Workflow name：本例为 `publish-to-pypi.yml`
   - Environment name：
     - TestPyPI 平台填写：`testpypi`
     - PyPI 平台填写：`pypi`
5. 点击 `ADD` 按钮

### 2. 配置仓库 Workflow

1. 新建 `.github/workflows/publish-to-pypi.yml` 文件
2. 填写文件内容，参考 [publish-to-pypi.yml](./publish-to-pypi.yml)
3. 注意修改 `PYPI_PROJECT_NAME` 为你的项目名称
4. 提交代码

### 3. 发布

1. 设置 tag，本例为 `v0.0.1`，具体执行 `git tag v0.0.1` 和 `git push origin v0.0.1`
2. 等待 Workflow 执行完成
3. GitHub 会自动生成 Release Notes，基于：
   - 合并的 Pull Requests
   - Commit 历史
   - Contributors 贡献

### 4. 验证

1. 打开 https://test.pypi.org/project/omni-pathlib/
2. 打开 https://pypi.org/project/omni-pathlib/
3. 查看 GitHub Releases 页面，确认 Release Notes 已自动生成

### 5. Release Notes 说明

该工作流使用 GitHub 的自动生成 Release Notes 功能，它会：
- 自动分类 PR（Features、Bug Fixes、Breaking Changes 等）
- 列出所有贡献者
- 显示完整的更改列表
- 无需手动维护 CHANGELOG.md 文件

如需自定义 Release Notes 格式，可以在仓库中创建 `.github/release.yml` 配置文件。

## Dependabot 自动合并

### 1. 功能说明

通过 `.github/dependabot.yml` 和 `.github/workflows/auto-merge-dependabot.yml` 配置，实现：
- 自动更新 GitHub Actions 依赖
- 自动批准和合并 Dependabot 创建的 PR（patch 和 minor 版本）
- Major 版本更新需要手动审查

### 2. 权限配置

**重要**：需要在仓库设置中启用 GitHub Actions 的写权限，否则自动合并功能无法正常工作。

配置步骤：
1. 进入仓库的 **Settings** 页面
2. 在左侧菜单中选择 **Actions** → **General**
3. 滚动到 **Workflow permissions** 部分
4. 选择 **Read and write permissions**
5. 勾选 **Allow GitHub Actions to create and approve pull requests**（可选，但推荐）
6. 点击 **Save** 保存设置

### 3. 自动合并策略

| 更新类型 | 版本示例 | 自动合并 | 说明 |
|---------|---------|---------|------|
| Patch | 1.0.1 → 1.0.2 | ✅ | 自动批准并合并 |
| Minor | 1.0.0 → 1.1.0 | ✅ | 自动批准并合并 |
| Major | 1.0.0 → 2.0.0 | ❌ | 需要手动审查和合并 |

### 4. 监控和管理

- **查看状态**：在 Actions 标签页查看 "Dependabot 自动合并" workflow 的运行状态
- **PR 标签**：自动合并的 PR 会显示 "Auto-merge enabled" 标签
- **手动干预**：可以随时在 PR 页面取消自动合并或手动合并
- **查看日志**：点击具体的 workflow 运行记录查看详细日志
