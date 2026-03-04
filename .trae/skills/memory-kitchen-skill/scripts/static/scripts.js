// 返回顶部按钮功能
const backToTopButton = document.createElement('a');
backToTopButton.href = '#';
backToTopButton.className = 'back-to-top';
backToTopButton.innerHTML = '↑';
document.body.appendChild(backToTopButton);

// 监听滚动事件
window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
        backToTopButton.classList.add('visible');
    } else {
        backToTopButton.classList.remove('visible');
    }
});

// 点击返回顶部
backToTopButton.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// 移动端菜单切换
const sidebarToggle = document.createElement('button');
sidebarToggle.className = 'sidebar-toggle';
sidebarToggle.textContent = '菜单';

const sidebar = document.querySelector('.sidebar');
if (sidebar) {
    sidebar.insertBefore(sidebarToggle, sidebar.firstChild);
    
    const sidebarContent = document.createElement('div');
    sidebarContent.className = 'sidebar-content';
    
    // 移动现有内容到新的容器
    while (sidebar.children.length > 1) {
        sidebarContent.appendChild(sidebar.children[1]);
    }
    
    sidebar.appendChild(sidebarContent);
    
    // 切换菜单显示/隐藏
    sidebarToggle.addEventListener('click', function() {
        sidebarContent.classList.toggle('active');
    });
}

// 搜索功能
function initSearch() {
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    searchContainer.innerHTML = `
        <input type="text" class="search-box" placeholder="搜索知识...">
    `;
    
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        const header = mainContent.querySelector('.header');
        if (header) {
            header.insertAdjacentElement('afterend', searchContainer);
        }
    }
    
    const searchBox = document.querySelector('.search-box');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const knowledgeItems = document.querySelectorAll('.knowledge-item, .topic');
            
            knowledgeItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
}

// 删除知识功能
function deleteKnowledge(knowledgeId, buttonElement) {
    if (!knowledgeId) {
        console.error('知识ID为空');
        return;
    }

    // 显示确认对话框
    const reason = prompt('请输入删除原因（可选）：\n1. 重复内容\n2. 信息错误\n3. 质量太低\n4. 其他');

    // 用户点击取消
    if (reason === null) {
        return;
    }

    // 确认删除
    if (!confirm('确定要删除这条知识吗？\n删除后可以在管理界面恢复。')) {
        return;
    }

    // 获取知识项元素
    const knowledgeItem = buttonElement.closest('.knowledge-item');
    if (!knowledgeItem) {
        console.error('找不到知识项元素');
        return;
    }

    // 获取知识标题
    const titleElement = knowledgeItem.querySelector('h2');
    const title = titleElement ? titleElement.textContent.trim() : '未知标题';

    // 发送删除请求到本地服务器（如果存在）
    // 由于这是静态HTML，我们使用 localStorage 来记录删除状态
    const deletedItems = JSON.parse(localStorage.getItem('deletedKnowledgeItems') || '[]');

    // 检查是否已存在
    const exists = deletedItems.some(item => {
        if (typeof item === 'object') {
            return item.id === knowledgeId;
        }
        return item === knowledgeId;
    });

    if (!exists) {
        deletedItems.push({
            id: knowledgeId,
            title: title,
            reason: reason,
            deletedAt: new Date().toISOString()
        });
        localStorage.setItem('deletedKnowledgeItems', JSON.stringify(deletedItems));
    }

    // 添加删除动画
    knowledgeItem.style.transition = 'all 0.3s ease';
    knowledgeItem.style.opacity = '0';
    knowledgeItem.style.transform = 'translateX(-100%)';

    setTimeout(() => {
        knowledgeItem.style.display = 'none';

        // 显示恢复提示
        showNotification('知识已删除', 'success', knowledgeId);
    }, 300);
}

// 恢复知识功能
function restoreKnowledge(knowledgeId) {
    const deletedItems = JSON.parse(localStorage.getItem('deletedKnowledgeItems') || '[]');
    const updatedItems = deletedItems.filter(item => {
        if (typeof item === 'object') {
            return item.id !== knowledgeId;
        }
        return item !== knowledgeId;
    });

    localStorage.setItem('deletedKnowledgeItems', JSON.stringify(updatedItems));

    // 刷新页面以显示恢复的知识
    window.location.reload();
}

// 显示通知
function showNotification(message, type = 'info', knowledgeId = null) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    let html = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    // 如果是删除通知，添加撤销按钮
    if (type === 'success' && knowledgeId) {
        html += `<button class="notification-undo" onclick="restoreKnowledge('${knowledgeId}'); this.parentElement.remove();">撤销</button>`;
    }

    notification.innerHTML = html;
    document.body.appendChild(notification);

    // 自动隐藏
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// 页面加载时隐藏已删除的知识
function hideDeletedItems() {
    const deletedItems = JSON.parse(localStorage.getItem('deletedKnowledgeItems') || '[]');
    const deletedIds = deletedItems.map(item => typeof item === 'object' ? item.id : item);

    document.querySelectorAll('.knowledge-item[data-id]').forEach(item => {
        const itemId = item.getAttribute('data-id');
        if (deletedIds.includes(itemId)) {
            item.style.display = 'none';
        }
    });
}

// 管理已删除的知识（显示管理界面）
function showDeletedItemsManager() {
    const deletedItems = JSON.parse(localStorage.getItem('deletedKnowledgeItems') || '[]');

    if (deletedItems.length === 0) {
        alert('没有已删除的知识');
        return;
    }

    // 创建管理界面
    const manager = document.createElement('div');
    manager.className = 'deleted-items-manager';
    manager.innerHTML = `
        <div class="manager-overlay" onclick="this.parentElement.remove()"></div>
        <div class="manager-content">
            <h2>已删除的知识 (${deletedItems.length} 条)</h2>
            <button class="manager-close" onclick="this.closest('.deleted-items-manager').remove()">×</button>
            <div class="deleted-list">
                ${deletedItems.map(item => {
                    const id = typeof item === 'object' ? item.id : item;
                    const title = typeof item === 'object' ? (item.title || '未知标题') : '未知标题';
                    const reason = typeof item === 'object' ? item.reason : '';
                    const time = typeof item === 'object' ? new Date(item.deletedAt).toLocaleString() : '';
                    // 截断标题，避免过长
                    const displayTitle = title.length > 50 ? title.substring(0, 50) + '...' : title;
                    return `
                        <div class="deleted-item">
                            <div class="deleted-info">
                                <span class="deleted-title" title="${title}">${displayTitle}</span>
                                ${reason ? `<span class="deleted-reason">原因: ${reason}</span>` : ''}
                                ${time ? `<span class="deleted-time">${time}</span>` : ''}
                            </div>
                            <button class="restore-btn" onclick="restoreKnowledge('${id}')">恢复</button>
                        </div>
                    `;
                }).join('')}
            </div>
            <button class="clear-all-btn" onclick="if(confirm('确定要清空所有已删除的知识吗？')) { localStorage.removeItem('deletedKnowledgeItems'); window.location.reload(); }">清空所有</button>
        </div>
    `;

    document.body.appendChild(manager);
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    initSearch();
    hideDeletedItems();

    // 添加管理按钮到页面
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        const managerBtn = document.createElement('button');
        managerBtn.className = 'manager-btn';
        managerBtn.textContent = '管理已删除';
        managerBtn.onclick = showDeletedItemsManager;

        const tocNav = sidebar.querySelector('.toc-nav ul');
        if (tocNav) {
            const li = document.createElement('li');
            li.appendChild(managerBtn);
            tocNav.appendChild(li);
        }
    }
});