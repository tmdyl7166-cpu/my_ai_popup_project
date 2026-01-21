/**
 * AI弹窗项目监控中心前端脚本
 * 提供实时监控、脚本控制、状态显示等功能
 */

// 全局变量
let socket;
let currentStatus = {};
let projects = [];
let scripts = [];
let logs = [];

// 初始化
document.addEventListener("DOMContentLoaded", function () {
  initSocket();
  loadInitialData();
  setupEventListeners();
  startPeriodicUpdates();
});

// 初始化Socket.IO连接
function initSocket() {
  socket = io();

  socket.on("connect", function () {
    console.log("Connected to server");
    updateStatusIndicator("connected");
  });

  socket.on("disconnect", function () {
    console.log("Disconnected from server");
    updateStatusIndicator("disconnected");
  });

  socket.on("status_update", function (data) {
    updateSystemStatus(data);
  });

  socket.on("script_result", function (data) {
    handleScriptResult(data);
  });

  socket.on("health_check_complete", function (data) {
    updateHealthScore(data);
  });
}

// 加载初始数据
async function loadInitialData() {
  try {
    // 并行加载数据
    const [statusResponse, scriptsResponse, logsResponse] = await Promise.all([
      fetch("/api/status"),
      fetch("/api/scripts"),
      fetch("/api/logs?lines=100"),
    ]);

    const statusData = await statusResponse.json();
    const scriptsData = await scriptsResponse.json();
    const logsData = await logsResponse.json();

    updateSystemStatus(statusData);
    updateScriptsList(scriptsData.scripts);
    updateLogsDisplay(logsData.logs);
  } catch (error) {
    console.error("Error loading initial data:", error);
    showAlert("加载数据失败", "danger");
  }
}

// 设置事件监听器
function setupEventListeners() {
  // 刷新按钮
  document.querySelectorAll('[onclick*="refreshAll"]').forEach((btn) => {
    btn.addEventListener("click", refreshAll);
  });

  // 日志行数选择
  document.getElementById("log-lines").addEventListener("change", function () {
    loadLogs();
  });
}

// 启动定期更新
function startPeriodicUpdates() {
  // 每30秒更新一次状态
  setInterval(updateSystemStatus, 30000);

  // 每60秒更新一次脚本列表
  setInterval(updateScriptsList, 60000);

  // 每10秒更新一次日志
  setInterval(loadLogs, 10000);
}

// 更新系统状态
function updateSystemStatus(data) {
  if (!data) return;

  currentStatus = data;

  // 更新CPU
  const cpuPercent = data.cpu_percent || 0;
  document.getElementById("cpu-progress").style.width = cpuPercent + "%";
  document.getElementById("cpu-text").textContent = cpuPercent.toFixed(1) + "%";

  // 更新内存
  const memoryPercent = data.memory_percent || 0;
  document.getElementById("memory-progress").style.width = memoryPercent + "%";
  document.getElementById("memory-text").textContent =
    memoryPercent.toFixed(1) + "%";

  // 更新磁盘
  const diskPercent = data.disk_percent || 0;
  document.getElementById("disk-progress").style.width = diskPercent + "%";
  document.getElementById("disk-text").textContent =
    diskPercent.toFixed(1) + "%";

  // 更新服务状态
  updateServiceStatus(data.services || {});
}

// 更新服务状态
function updateServiceStatus(services) {
  const indicator = document.getElementById("status-indicator");
  const icon = indicator.querySelector("i");

  // 检查是否有服务异常
  const hasErrors = Object.values(services).some(
    (status) => status !== "running",
  );

  if (hasErrors) {
    icon.className = "fas fa-circle text-warning";
    indicator.querySelector("span:last-child").textContent = "服务异常";
  } else {
    icon.className = "fas fa-circle text-success";
    indicator.querySelector("span:last-child").textContent = "系统正常";
  }
}

// 更新项目列表
function updateProjectsList(projects) {
  const container = document.getElementById("projects-container");
  container.innerHTML = "";

  if (!projects || projects.length === 0) {
    container.innerHTML =
      '<div class="text-center text-muted">暂无项目数据</div>';
    return;
  }

  projects.forEach((project) => {
    const projectCard = createProjectCard(project);
    container.appendChild(projectCard);
  });
}

// 创建项目卡片
function createProjectCard(project) {
  const card = document.createElement("div");
  card.className = "project-card fade-in";

  const statusClass = getStatusClass(project.status);
  const statusText = getStatusText(project.status);

  card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div class="flex-grow-1">
                <div class="project-name">${project.name || "未知项目"}</div>
                <div class="project-status status-${statusClass}">${statusText}</div>
                <div class="project-description">${project.description || "暂无描述"}</div>
            </div>
            <div class="project-actions">
                <button class="btn btn-outline-primary btn-sm me-1" onclick="viewProjectDetails('${project.id}')">
                    <i class="fas fa-info-circle"></i>
                </button>
                <button class="btn btn-outline-success btn-sm" onclick="runProjectAction('${project.id}', 'restart')">
                    <i class="fas fa-play"></i>
                </button>
            </div>
        </div>
        ${project.metrics ? createMetricsDisplay(project.metrics) : ""}
    `;

  return card;
}

// 创建指标显示
function createMetricsDisplay(metrics) {
  return `
        <div class="mt-2">
            <small class="text-muted">
                CPU: ${metrics.cpu || 0}% |
                内存: ${metrics.memory || 0}MB |
                QPS: ${metrics.qps || 0}
            </small>
        </div>
    `;
}

// 获取状态样式类
function getStatusClass(status) {
  const statusMap = {
    running: "running",
    stopped: "stopped",
    warning: "warning",
    error: "error",
  };
  return statusMap[status] || "stopped";
}

// 获取状态文本
function getStatusText(status) {
  const statusMap = {
    running: "运行中",
    stopped: "已停止",
    warning: "警告",
    error: "错误",
  };
  return statusMap[status] || "未知";
}

// 更新脚本列表
function updateScriptsList(scriptsData) {
  scripts = scriptsData || [];
  const container = document.getElementById("scripts-container");

  if (!scripts || scripts.length === 0) {
    container.innerHTML = '<div class="text-center text-muted">暂无脚本</div>';
    return;
  }

  container.innerHTML = "";
  scripts.forEach((script) => {
    const scriptItem = createScriptItem(script);
    container.appendChild(scriptItem);
  });
}

// 创建脚本项
function createScriptItem(script) {
  const item = document.createElement("div");
  item.className = "script-item";

  const sizeKB = (script.size / 1024).toFixed(1);
  const modified = new Date(script.modified).toLocaleString();

  item.innerHTML = `
        <div class="script-name">${script.name}</div>
        <div class="script-size">${sizeKB} KB</div>
        <button class="btn btn-outline-success btn-sm script-run-btn" onclick="runScript('${script.name}')">
            <i class="fas fa-play"></i>
        </button>
    `;

  // 添加工具提示
  item.title = `修改时间: ${modified}\n路径: ${script.path}`;

  return item;
}

// 更新日志显示
function updateLogsDisplay(logsData) {
  logs = logsData || [];
  const container = document.getElementById("logs-container");

  if (!logs || logs.length === 0) {
    container.textContent = "暂无日志数据";
    return;
  }

  container.textContent = logs.join("\n");
  // 自动滚动到底部
  container.scrollTop = container.scrollHeight;
}

// 加载日志
async function loadLogs() {
  try {
    const lines = document.getElementById("log-lines").value;
    const response = await fetch(`/api/logs?lines=${lines}`);
    const data = await response.json();
    updateLogsDisplay(data.logs);
  } catch (error) {
    console.error("Error loading logs:", error);
  }
}

// 运行脚本
async function runScript(scriptName) {
  showLoading("正在运行脚本...");

  try {
    const response = await fetch(`/api/scripts/${scriptName}/run`, {
      method: "POST",
    });

    if (response.ok) {
      showAlert(`脚本 ${scriptName} 已开始运行`, "success");
    } else {
      const error = await response.text();
      showAlert(`运行脚本失败: ${error}`, "danger");
    }
  } catch (error) {
    console.error("Error running script:", error);
    showAlert("运行脚本失败", "danger");
  } finally {
    hideLoading();
  }
}

// 运行自定义脚本
function runCustomScript() {
  const scriptName = document.getElementById("custom-script").value.trim();
  if (scriptName) {
    runScript(scriptName);
    document.getElementById("custom-script").value = "";
  } else {
    showAlert("请输入脚本名称", "warning");
  }
}

// 运行健康检查
async function runHealthCheck() {
  showLoading("正在进行健康检查...");

  try {
    const response = await fetch("/api/health", { method: "POST" });
    const result = await response.json();

    if (response.ok) {
      updateHealthScore(result);
      showAlert("健康检查完成", "success");
    } else {
      showAlert("健康检查失败", "danger");
    }
  } catch (error) {
    console.error("Error running health check:", error);
    showAlert("健康检查失败", "danger");
  } finally {
    hideLoading();
  }
}

// 更新健康评分
function updateHealthScore(data) {
  const scoreElement = document.getElementById("health-score");
  const progressElement = document.getElementById("health-progress");
  const statusElement = document.getElementById("health-status");

  if (!data || !data.summary) return;

  const score = data.summary.health_score || 0;
  scoreElement.textContent = score.toFixed(1);

  progressElement.style.width = score + "%";

  // 更新颜色
  progressElement.className = "progress-bar";
  if (score >= 90) {
    progressElement.classList.add("health-excellent");
    statusElement.textContent = "优秀";
  } else if (score >= 70) {
    progressElement.classList.add("health-good");
    statusElement.textContent = "良好";
  } else if (score >= 50) {
    progressElement.classList.add("health-warning");
    statusElement.textContent = "警告";
  } else {
    progressElement.classList.add("health-critical");
    statusElement.textContent = "严重";
  }
}

// 查看项目详情
function viewProjectDetails(projectId) {
  // 这里可以打开项目详情模态框
  showAlert(`查看项目 ${projectId} 详情`, "info");
}

// 运行项目操作
function runProjectAction(projectId, action) {
  showAlert(`执行项目 ${projectId} 的 ${action} 操作`, "info");
  // 这里可以调用后端API
}

// 处理脚本结果
function handleScriptResult(data) {
  const title = `脚本 ${data.script} 执行结果`;
  const content = `
返回码: ${data.return_code}

标准输出:
${data.stdout || "无"}

标准错误:
${data.stderr || "无"}
    `;

  showResultModal(title, content);
}

// 显示加载动画
function showLoading(text = "加载中...") {
  document.getElementById("loading-text").textContent = text;
  const modal = new bootstrap.Modal(document.getElementById("loadingModal"));
  modal.show();
}

// 隐藏加载动画
function hideLoading() {
  const modal = bootstrap.Modal.getInstance(
    document.getElementById("loadingModal"),
  );
  if (modal) {
    modal.hide();
  }
}

// 显示结果模态框
function showResultModal(title, content) {
  document.getElementById("result-title").textContent = title;
  document.getElementById("result-content").textContent = content;
  const modal = new bootstrap.Modal(document.getElementById("resultModal"));
  modal.show();
}

// 显示提示消息
function showAlert(message, type = "info") {
  // 使用Bootstrap Toast或Alert显示消息
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText =
    "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  document.body.appendChild(alertDiv);

  // 3秒后自动消失
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 3000);
}

// 更新状态指示器
function updateStatusIndicator(status) {
  const indicator = document.getElementById("status-indicator");
  const icon = indicator.querySelector("i");
  const text = indicator.querySelector("span:last-child");

  if (status === "connected") {
    icon.className = "fas fa-circle text-success";
    text.textContent = "已连接";
  } else {
    icon.className = "fas fa-circle text-danger";
    text.textContent = "未连接";
  }
}

// 刷新所有数据
function refreshAll() {
  loadInitialData();
  showAlert("数据已刷新", "success");
}

// 页面卸载时清理
window.addEventListener("beforeunload", function () {
  if (socket) {
    socket.disconnect();
  }
});
