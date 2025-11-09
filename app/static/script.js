let selectedDocumentId = null;
let searchMode = 'all';

document.addEventListener('DOMContentLoaded', function() {
    loadDocuments();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('uploadBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);
    
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    document.getElementById('chatInput').addEventListener('input', autoResizeTextarea);
    
    document.querySelectorAll('input[name="docFilter"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            searchMode = e.target.value;
            updateSelectedDocInfo();
        });
    });
}

function autoResizeTextarea() {
    const textarea = document.getElementById('chatInput');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span>⏳</span> Загрузка...';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Ошибка при загрузке файла');
        }
        
        const result = await response.json();
        showNotification(result.message, 'success');
        
        await loadDocuments();
        
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span>📁</span> Загрузить файл';
        event.target.value = '';
    }
}

async function loadDocuments() {
    const documentList = document.getElementById('documentList');
    
    try {
        documentList.innerHTML = '<div class="loading">Загрузка документов...</div>';
        
        const response = await fetch('/api/documents');
        if (!response.ok) {
            throw new Error('Ошибка при загрузке документов');
        }
        
        const documents = await response.json();
        
        if (documents.length === 0) {
            documentList.innerHTML = '<div class="loading">Нет загруженных документов</div>';
            return;
        }
        
        documentList.innerHTML = '';
        
        documents.forEach(doc => {
            const docElement = createDocumentElement(doc);
            documentList.appendChild(docElement);
        });
        
    } catch (error) {
        documentList.innerHTML = `<div class="error">Ошибка: ${error.message}</div>`;
    }
}

function createDocumentElement(doc) {
    const div = document.createElement('div');
    div.className = 'document-item';
    if (doc.id === selectedDocumentId) {
        div.classList.add('selected');
    }
    
    const uploadDate = new Date(doc.upload_date).toLocaleString('ru-RU');
    const fileSize = formatFileSize(doc.file_size);
    
    div.innerHTML = `
        <div class="document-name">${doc.filename}</div>
        <div class="document-info">
            <span>${fileSize}</span>
            <span>${doc.chunk_count} фрагментов</span>
        </div>
        <div class="document-info">
            <span style="font-size: 11px;">${uploadDate}</span>
        </div>
        <div class="document-actions">
            <button class="btn btn-small btn-delete" data-id="${doc.id}">Удалить</button>
        </div>
    `;
    
    div.addEventListener('click', (e) => {
        if (!e.target.classList.contains('btn-delete')) {
            selectDocument(doc.id);
        }
    });
    
    div.querySelector('.btn-delete').addEventListener('click', (e) => {
        e.stopPropagation();
        deleteDocument(doc.id);
    });
    
    return div;
}

function selectDocument(documentId) {
    if (selectedDocumentId === documentId) {
        selectedDocumentId = null;
    } else {
        selectedDocumentId = documentId;
        searchMode = 'selected';
        document.querySelector('input[name="docFilter"][value="selected"]').checked = true;
    }
    
    document.querySelectorAll('.document-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    if (selectedDocumentId) {
        const selectedElement = document.querySelector(`[data-id="${documentId}"]`)?.closest('.document-item');
        if (selectedElement) {
            selectedElement.classList.add('selected');
        }
    }
    
    updateSelectedDocInfo();
}

function updateSelectedDocInfo() {
    const infoElement = document.getElementById('selectedDocInfo');
    
    if (searchMode === 'selected' && selectedDocumentId) {
        const docElement = document.querySelector(`[data-id="${selectedDocumentId}"]`)?.closest('.document-item');
        if (docElement) {
            const docName = docElement.querySelector('.document-name').textContent;
            infoElement.textContent = `🎯 Поиск в документе: ${docName}`;
            infoElement.style.display = 'block';
        }
    } else {
        infoElement.style.display = 'none';
    }
}

async function deleteDocument(documentId) {
    if (!confirm('Вы уверены, что хотите удалить этот документ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/documents/${documentId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Ошибка при удалении документа');
        }
        
        const result = await response.json();
        showNotification(result.message, 'success');
        
        if (selectedDocumentId === documentId) {
            selectedDocumentId = null;
            updateSelectedDocInfo();
        }
        
        await loadDocuments();
        
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const query = input.value.trim();
    
    if (!query) return;
    
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    // Отладочное логирование
    console.log('[DEBUG] Query:', query);
    console.log('[DEBUG] Query lowercase:', query.toLowerCase());
    console.log('[DEBUG] Query length:', query.length);
    console.log('[DEBUG] Checking referat:', query.toLowerCase() === 'referat', query.toLowerCase() === 'реферат');
    
    addMessage(query, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    // Проверяем, является ли запрос командой суммаризации
    if (query.toLowerCase() === 'summary' || query.toLowerCase() === 'суммаризация') {
        await handleSummarization();
        sendBtn.disabled = false;
        return;
    }
    
    // Проверяем, является ли запрос командой реферативного перевода
    if (query.toLowerCase() === 'referat' || query.toLowerCase() === 'реферат') {
        await handleReferat();
        sendBtn.disabled = false;
        return;
    }
    
    const loadingMessage = addMessage('Думаю...', 'assistant', true);
    
    try {
        const requestBody = {
            query: query
            // context_limit не передаем - будет использовано значение по умолчанию из настроек (7)
        };
        
        if (searchMode === 'selected' && selectedDocumentId) {
            requestBody.document_id = selectedDocumentId;
        }
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка при получении ответа');
        }
        
        const result = await response.json();
        
        loadingMessage.remove();
        
        addMessage(result.answer, 'assistant', false, result.sources);
        
    } catch (error) {
        loadingMessage.remove();
        addMessage(`Ошибка: ${error.message}`, 'assistant');
        showNotification(`Ошибка: ${error.message}`, 'error');
    } finally {
        sendBtn.disabled = false;
    }
}

async function handleSummarization() {
    if (!selectedDocumentId) {
        addMessage('⚠️ Пожалуйста, выберите документ для суммаризации.', 'assistant');
        showNotification('Выберите документ из списка слева', 'error');
        return;
    }
    
    const loadingMessage = addMessage('Генерирую краткое содержание документа...', 'assistant', true);
    
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_id: selectedDocumentId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при суммаризации');
        }
        
        const result = await response.json();
        
        loadingMessage.remove();
        
        // Добавляем заголовок с информацией о документе
        const summaryWithHeader = `## 📄 Краткое содержание документа\n\n**Документ:** ${result.filename}\n**Фрагментов:** ${result.chunk_count}\n\n---\n\n${result.summary}`;
        
        addMessage(summaryWithHeader, 'assistant');
        showNotification('Суммаризация завершена', 'success');
        
    } catch (error) {
        loadingMessage.remove();
        addMessage(`❌ Ошибка при суммаризации: ${error.message}`, 'assistant');
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

async function handleReferat() {
    if (!selectedDocumentId) {
        addMessage('⚠️ Пожалуйста, выберите документ для создания реферативного перевода.', 'assistant');
        showNotification('Выберите документ из списка слева', 'error');
        return;
    }
    
    const loadingMessage = addMessage('⏳ Создаю реферативный перевод документа...\n\nЭто может занять несколько минут для больших документов.', 'assistant', true);
    
    try {
        const response = await fetch('/api/referat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_id: selectedDocumentId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при создании реферативного перевода');
        }
        
        const result = await response.json();
        
        loadingMessage.remove();
        
        // Формируем полный URL для скачивания PDF с правильным кодированием
        let fullPdfUrl;
        if (result.pdf_url.startsWith('http')) {
            fullPdfUrl = result.pdf_url;
        } else {
            // Разбиваем путь на части и кодируем каждую часть отдельно
            const pathParts = result.pdf_url.split('/').filter(p => p.length > 0);
            const encodedParts = pathParts.map(part => encodeURIComponent(part));
            const encodedPath = '/' + encodedParts.join('/');
            fullPdfUrl = `${window.location.origin}${encodedPath}`;
        }
        
        console.log('PDF URL:', result.pdf_url);
        console.log('Full PDF URL:', fullPdfUrl);
        
        // Добавляем сообщение с ссылкой на скачивание PDF
        const referatMessage = `## 📚 Реферативный перевод документа\n\n**Документ:** ${result.filename}\n**Фрагментов:** ${result.chunk_count}\n\n✅ **Реферативный перевод успешно создан!**\n\n📥 [**Скачать PDF**](${fullPdfUrl})\n\n---\n\n### Предпросмотр:\n\n${result.referat.substring(0, 500)}...\n\n*[Полный текст доступен в PDF файле]*`;
        
        addMessage(referatMessage, 'assistant');
        showNotification('Реферативный перевод готов! Файл доступен для скачивания.', 'success');
        
    } catch (error) {
        loadingMessage.remove();
        addMessage(`❌ Ошибка при создании реферативного перевода: ${error.message}`, 'assistant');
        showNotification(`Ошибка: ${error.message}`, 'error');
    }
}

function addMessage(text, sender, isLoading = false, sources = null) {
    const messagesContainer = document.getElementById('chatMessages');
    
    const welcomeMessage = messagesContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${sender}`;
    
    // Рендерим Markdown для сообщений ассистента
    let messageContent = text;
    if (sender === 'assistant' && !isLoading) {
        if (typeof marked !== 'undefined') {
            try {
                console.log('Rendering Markdown for assistant message');
                messageContent = marked.parse(text);
                console.log('Markdown rendered successfully');
            } catch (e) {
                console.error('Ошибка рендеринга Markdown:', e);
                messageContent = text.replace(/\n/g, '<br>');
            }
        } else {
            console.warn('marked.js не загружен, используем простую замену переносов');
            messageContent = text.replace(/\n/g, '<br>');
        }
    } else if (sender === 'user') {
        // Для сообщений пользователя просто заменяем переносы строк
        messageContent = text.replace(/\n/g, '<br>');
    }
    
    let content = `<div class="message-content">${messageContent}</div>`;
    
    if (sources && sources.length > 0) {
        content += '<div class="message-sources">';
        content += '<h4>Источники:</h4>';
        sources.forEach((source, idx) => {
            content += `<div class="source-item">
                ${idx + 1}. ${source.filename} (совпадение: ${(source.similarity * 100).toFixed(1)}%)
            </div>`;
        });
        content += '</div>';
    }
    
    messageDiv.innerHTML = content;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageDiv;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
}

