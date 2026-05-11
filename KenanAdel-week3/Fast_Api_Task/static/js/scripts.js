// ---------------------------------
        // 1. Core State & Configuration
        // ---------------------------------
        const API_BASE_URL = window.location.origin; // e.g., "http://127.0.0.1:8000"
        let currentToken = localStorage.getItem("jwt_token"); // Check if user logged in previously

        // Run this when the page loads
        document.addEventListener("DOMContentLoaded", () => {
            if (currentToken) {
                // User has a token, skip login!
                showDashboard();
            } else {
                // User has NO token, show login screen.
                showLogin();
            }

            // Setup Sidebar Toggle
            document.getElementById('sidebarCollapse').addEventListener('click', function () {
                // Unified toggle logic for both Mobile and Desktop
                document.getElementById('sidebar').classList.toggle('active');
                document.getElementById('main-content').classList.toggle('active');
            });

            // Close sidebar when clicking outside on mobile
            document.getElementById('main-content').addEventListener('click', function () {
                if (window.innerWidth <= 768) {
                    document.getElementById('sidebar').classList.remove('active');
                }
            });
        });

        // ---------------------------------
        // 2. Authentication Logic
        // ---------------------------------
        async function handleLogin(event) {
            event.preventDefault(); // Stop page from reloading
            showLoader();

            const username = document.getElementById("usernameInput").value;
            const password = document.getElementById("passwordInput").value;

            // FastAPI's OAuth2 expects data as "application/x-www-form-urlencoded"
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);

            try {
                // Send the Login Request to the Backend
                const response = await fetch(`${API_BASE_URL}/users/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    currentToken = data.access_token;
                    // Save the token so they don't have to login again after refreshing
                    localStorage.setItem("jwt_token", currentToken);
                    showToast("Login Successful!", "success");
                    showDashboard();
                } else {
                    const err = await response.json();
                    showToast(err.detail || "Login Failed", "danger");
                }
            } catch (error) {
                showToast("Connection Error", "danger");
            }

            hideLoader();
        }

        function logout() {
            // Simply remove the token and show the login screen
            localStorage.removeItem("jwt_token");
            currentToken = null;
            showLogin();
        }

        // ---------------------------------
        // 3. UI Helpers
        // ---------------------------------
        function showLogin() {
            document.getElementById("loginSection").classList.remove("hidden");
            document.getElementById("dashboardSection").classList.add("hidden");
        }

        function showDashboard() {
            document.getElementById("loginSection").classList.add("hidden");
            document.getElementById("dashboardSection").classList.remove("hidden");
            // Load initial data for default view (Users)
            fetchUsers();
        }

        function switchView(viewId, linkElement) {
            // Hide all views
            document.getElementById("usersView").classList.add("hidden");
            document.getElementById("projectsView").classList.add("hidden");
            document.getElementById("tasksView").classList.add("hidden");

            // Show the requested view
            document.getElementById(viewId).classList.remove("hidden");

            // Update sidebar active link styling
            const links = document.getElementById("sidebar").getElementsByTagName("a");
            for (let link of links) {
                link.classList.remove("active");
            }
            linkElement.classList.add("active");

            // Load data for the selected view
            if (viewId === 'usersView') fetchUsers();
            if (viewId === 'projectsView') {
                fetchProjects();
                populateProjectOwnerDropdown();
            }
            if (viewId === 'tasksView') {
                fetchTasks();
                populateTaskProjectDropdown();
            }
        }

        function showLoader() {
            document.getElementById("loader").classList.remove("hidden");
        }

        function hideLoader() {
            document.getElementById("loader").classList.add("hidden");
        }

        function showToast(message, type = "success") {
            const toastEl = document.getElementById("liveToast");
            const toastMessage = document.getElementById("toastMessage");

            toastMessage.textContent = message;

            // Change color based on success/error
            toastEl.className = `toast align-items-center text-bg-${type} border-0`;

            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        }

        // Helper function for fetch rules: adding Authorization header automatically
        async function fetchWithAuth(url, options = {}) {
            const headers = options.headers || {};
            if (currentToken) {
                headers["Authorization"] = `Bearer ${currentToken}`; // Include JWT Token!
            }
            options.headers = headers;

            const response = await fetch(url, options);
            if (response.status === 401) {
                // Token is invalid or expired
                showToast("Session expired. Please login again.", "danger");
                logout();
                throw new Error("Unauthorized");
            }
            return response;
        }

        // ---------------------------------
        // 4. Data Operations (CRUD)
        // ---------------------------------

        // --- READ/CREATE/UPDATE/DELETE USERS ---
        async function fetchUsers() {
            showLoader();
            try {
                const response = await fetchWithAuth(`${API_BASE_URL}/users/`);
                const users = await response.json();

                const tableBody = document.getElementById("usersTableBody");
                tableBody.innerHTML = "";

                if (users.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted"><i class="fas fa-inbox fa-3x mb-3 d-block"></i>No Users Found</td></tr>`;
                } else {
                    users.forEach(user => {
                        tableBody.innerHTML += `
                            <tr>
                                <td>#${user.id}</td>
                                <td class="fw-bold">${user.username}</td>
                                <td>${user.email}</td>
                                <td>
                                    <span class="badge ${user.is_active ? 'bg-success' : 'bg-danger'}">
                                        ${user.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick='openEditUserModal(${JSON.stringify(user)})'><i class="fas fa-edit"></i> Edit</button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id})"><i class="fas fa-trash"></i> Delete</button>
                                </td>
                            </tr>
                        `;
                    });
                }
            } catch (error) {
                console.error("Error fetching users", error);
            }
            hideLoader();
        }

        function openEditUserModal(user) {
            document.getElementById('userModalTitle').innerText = 'Edit User';
            document.getElementById('userId').value = user.id;
            document.getElementById('userUsername').value = user.username;
            document.getElementById('userEmail').value = user.email;
            document.getElementById('userIsActive').checked = user.is_active;

            // Hide/Disable password as we don't handle password updates through this endpoint in this simple version
            document.getElementById('userPasswordGroup').classList.add('hidden');
            document.getElementById('userPassword').required = false;

            const modal = new bootstrap.Modal(document.getElementById('userModal'));
            modal.show();
        }

        // Setup the modal cleanly for 'New User' requests
        document.getElementById('userModal').addEventListener('hidden.bs.modal', function () {
            document.getElementById('userForm').reset();
            document.getElementById('userId').value = '';
            document.getElementById('userModalTitle').innerText = 'Create New User';

            document.getElementById('userPasswordGroup').classList.remove('hidden');
            document.getElementById('userPassword').required = true;
        });

        async function saveUser(event) {
            event.preventDefault();
            const userId = document.getElementById('userId').value;
            const isEditing = !!userId;

            const data = {
                username: document.getElementById('userUsername').value,
                email: document.getElementById('userEmail').value,
                is_active: document.getElementById('userIsActive').checked
            };

            let url = `${API_BASE_URL}/users/`;
            let method = "POST";

            if (isEditing) {
                url = `${API_BASE_URL}/users/${userId}`;
                method = "PUT";
            } else {
                data.password = document.getElementById('userPassword').value;
            }

            // Using fetch directly as we need dynamic method
            showLoader();
            try {
                const response = await fetchWithAuth(url, {
                    method: method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showToast(isEditing ? "User Updated!" : "User Created!", "success");
                    const bsModal = bootstrap.Modal.getInstance(document.getElementById('userModal')) || new bootstrap.Modal(document.getElementById('userModal'));
                    bsModal.hide();
                    fetchUsers();
                } else {
                    const err = await response.json();
                    showToast(err.detail || "Error occurred", "danger");
                }
            } catch (error) {
                showToast("Connection Error", "danger");
            }
            hideLoader();
        }

        // --- REUSABLE DELETE LOGIC ---
        let deleteTargetUrl = "";
        let deleteRefreshCallback = null;

        function openDeleteConfirmModal(endpoint, id, itemName, refreshCallback) {
            deleteTargetUrl = `${API_BASE_URL}/${endpoint}/${parseInt(id)}`;
            deleteRefreshCallback = refreshCallback;
            document.getElementById('deleteConfirmMessage').innerText = `Do you really want to delete this ${itemName}?`;

            const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
            modal.show();
        }

        document.getElementById('confirmDeleteBtn').addEventListener('click', async function () {
            const bsModal = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal'));
            bsModal.hide();
            showLoader();
            try {
                const response = await fetchWithAuth(deleteTargetUrl, { method: "DELETE" });
                if (response.ok) {
                    showToast("Record Deleted successfully", "success");
                    if (deleteRefreshCallback) window[deleteRefreshCallback]();
                } else {
                    const err = await response.json();
                    showToast(err.detail || "Failed to delete record", "danger");
                }
            } catch (error) {
                showToast("Connection Error", "danger");
            }
            hideLoader();
        });


        // --- DELETE USER ---
        function deleteUser(id) {
            openDeleteConfirmModal('users', id, 'user', 'fetchUsers');
        }

        // --- READ/POPULATE USERS DROPDOWN ---
        async function populateProjectOwnerDropdown() {
            try {
                const response = await fetchWithAuth(`${API_BASE_URL}/users/`);
                const users = await response.json();

                const projOwnerSelect = document.getElementById("projOwner");
                projOwnerSelect.innerHTML = '<option value="">Select an Owner...</option>';

                users.forEach(user => {
                    // Only show active users in the dropdown
                    if (user.is_active) {
                        projOwnerSelect.innerHTML += `<option value="${user.id}">${user.username}</option>`;
                    }
                });
            } catch (error) {
                console.error("Error fetching users for dropdown", error);
                document.getElementById("projOwner").innerHTML = '<option value="">Error loading users</option>';
            }
        }

        // --- READ/POPULATE PROJECTS DROPDOWN ---
        async function populateTaskProjectDropdown() {
            try {
                const response = await fetchWithAuth(`${API_BASE_URL}/projects/`);
                const projects = await response.json();

                const taskProjectSelect = document.getElementById("taskProjectId");
                taskProjectSelect.innerHTML = '<option value="">Select a Project...</option>';

                projects.forEach(project => {
                    taskProjectSelect.innerHTML += `<option value="${project.id}">${project.title}</option>`;
                });
            } catch (error) {
                console.error("Error fetching projects for dropdown", error);
                document.getElementById("taskProjectId").innerHTML = '<option value="">Error loading projects</option>';
            }
        }

        // --- READ PROJECTS ---
        async function fetchProjects() {
            showLoader();
            try {
                const response = await fetchWithAuth(`${API_BASE_URL}/projects/`);
                const projects = await response.json();

                const tableBody = document.getElementById("projectsTableBody");
                tableBody.innerHTML = ""; // Clear old rows

                if (projects.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted"><i class="fas fa-folder-open fa-3x mb-3 d-block"></i>No Projects Found</td></tr>`;
                } else {
                    projects.forEach(project => {
                        const ownerName = project.owner ? project.owner.username : `User ID: ${project.owner_id}`;
                        tableBody.innerHTML += `
                            <tr>
                                <td>#${project.id}</td>
                                <td class="fw-bold text-wrap-title">${project.title}</td>
                                <td class="text-muted"><span class="text-truncate-desc" title="${(project.description || '').replace(/"/g, '&quot;')}">${project.description || '-'}</span></td>
                                <td><span class="badge bg-info text-dark">${ownerName}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick='openEditProjectModal(${JSON.stringify(project).replace(/'/g, "&#39;")})'><i class="fas fa-edit"></i> Edit</button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProject(${project.id})"><i class="fas fa-trash"></i> Delete</button>
                                </td>
                            </tr>
                        `;
                    });
                }
            } catch (error) {
                console.error("Error fetching projects", error);
            }
            hideLoader();
        }

        function openEditProjectModal(project) {
            // Populate the dropdown first, just in case
            populateProjectOwnerDropdown().then(() => {
                document.getElementById('projectModalTitle').innerText = 'Edit Project';
                document.getElementById('projId').value = project.id;
                document.getElementById('projTitle').value = project.title;
                document.getElementById('projDesc').value = project.description || '';
                document.getElementById('projOwner').value = project.owner_id;

                const modal = new bootstrap.Modal(document.getElementById('projectModal'));
                modal.show();
            });
        }

        // Setup the modal cleanly for 'New Project' requests
        document.getElementById('projectModal').addEventListener('hidden.bs.modal', function () {
            document.getElementById('projectForm').reset();
            document.getElementById('projId').value = '';
            document.getElementById('projectModalTitle').innerText = 'Create New Project';
        });

        // --- CREATE/UPDATE PROJECT ---
        async function saveProject(event) {
            event.preventDefault();

            const projectId = document.getElementById('projId').value;
            const isEditing = !!projectId;

            const data = {
                title: document.getElementById("projTitle").value,
                description: document.getElementById("projDesc").value,
                owner_id: parseInt(document.getElementById("projOwner").value)
            };

            let url = `${API_BASE_URL}/projects/`;
            let method = "POST";

            if (isEditing) {
                url = `${API_BASE_URL}/projects/${projectId}`;
                method = "PUT";
            }

            showLoader();
            try {
                const response = await fetchWithAuth(url, {
                    method: method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showToast(isEditing ? "Project Updated!" : "Project Created!", "success");
                    const bsModal = bootstrap.Modal.getInstance(document.getElementById('projectModal')) || new bootstrap.Modal(document.getElementById('projectModal'));
                    bsModal.hide();
                    fetchProjects();
                } else {
                    const err = await response.json();
                    showToast(err.detail || "Error occurred", "danger");
                }
            } catch (error) {
                showToast("Connection Error", "danger");
            }
            hideLoader();
        }

        // --- DELETE PROJECT ---
        function deleteProject(id) {
            openDeleteConfirmModal('projects', id, 'project', 'fetchProjects');
        }

        // --- READ TASKS ---
        async function fetchTasks() {
            showLoader();
            try {
                const response = await fetchWithAuth(`${API_BASE_URL}/tasks/`);
                const tasks = await response.json();

                const tableBody = document.getElementById("tasksTableBody");
                tableBody.innerHTML = "";

                if (tasks.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted"><i class="fas fa-clipboard-check fa-3x mb-3 d-block"></i>No Tasks Found</td></tr>`;
                } else {
                    tasks.forEach(task => {
                        const projectName = task.project ? task.project.title : `Project ID: ${task.project_id}`;
                        let badgeClass = "bg-secondary";
                        if (task.status === "completed") badgeClass = "bg-success";
                        if (task.status === "in_progress") badgeClass = "bg-warning text-dark";

                        tableBody.innerHTML += `
                            <tr>
                                <td>#${task.id}</td>
                                <td class="fw-bold text-wrap-title">${task.title}</td>
                                <td class="text-muted"><span class="text-truncate-desc" title="${(task.description || '').replace(/"/g, '&quot;')}">${task.description || '-'}</span></td>
                                <td><span class="badge ${badgeClass}">${task.status.replace("_", " ").toUpperCase()}</span></td>
                                <td><span class="badge bg-primary text-wrap-title">${projectName}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick='openEditTaskModal(${JSON.stringify(task).replace(/'/g, "&#39;")})'><i class="fas fa-edit"></i> Edit</button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})"><i class="fas fa-trash"></i> Delete</button>
                                </td>
                            </tr>
                        `;
                    });
                }
            } catch (error) {
                console.error("Error fetching tasks", error);
            }
            hideLoader();
        }

        function openEditTaskModal(task) {
            populateTaskProjectDropdown().then(() => {
                document.getElementById('taskModalTitle').innerText = 'Edit Task';
                document.getElementById('taskId').value = task.id;
                document.getElementById('taskTitle').value = task.title;
                document.getElementById('taskDesc').value = task.description || '';
                document.getElementById('taskProjectId').value = task.project_id;
                document.getElementById('taskStatus').value = task.status || 'pending';

                const modal = new bootstrap.Modal(document.getElementById('taskModal'));
                modal.show();
            });
        }

        document.getElementById('taskModal').addEventListener('hidden.bs.modal', function () {
            document.getElementById('taskForm').reset();
            document.getElementById('taskId').value = '';
            document.getElementById('taskModalTitle').innerText = 'Create New Task';
            document.getElementById('taskStatus').value = 'pending';
        });

        // --- CREATE/UPDATE TASK ---
        async function saveTask(event) {
            event.preventDefault();

            const taskId = document.getElementById('taskId').value;
            const isEditing = !!taskId;

            const data = {
                title: document.getElementById("taskTitle").value,
                description: document.getElementById("taskDesc").value,
                project_id: parseInt(document.getElementById("taskProjectId").value),
                status: document.getElementById("taskStatus").value
            };

            let url = `${API_BASE_URL}/tasks/`;
            let method = "POST";

            if (isEditing) {
                url = `${API_BASE_URL}/tasks/${taskId}`;
                method = "PUT";
            }

            showLoader();
            try {
                const response = await fetchWithAuth(url, {
                    method: method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showToast(isEditing ? "Task Updated!" : "Task Created!", "success");
                    const bsModal = bootstrap.Modal.getInstance(document.getElementById('taskModal')) || new bootstrap.Modal(document.getElementById('taskModal'));
                    bsModal.hide();
                    fetchTasks();
                } else {
                    const err = await response.json();
                    showToast(err.detail || "Error occurred", "danger");
                }
            } catch (error) {
                showToast("Connection Error", "danger");
            }
            hideLoader();
        }

        // --- DELETE TASK ---
        function deleteTask(id) {
            openDeleteConfirmModal('tasks', id, 'task', 'fetchTasks');
        }

        // Shared Create Action Function to keep code clean
        async function sendCreateRequestContext(url, payload, modalElement, refreshFunction) {
            showLoader();
            try {
                const response = await fetchWithAuth(url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    showToast("Successfully Created!", "success");
                    // Hide the Modal using Bootstrap JS
                    const bsModal = bootstrap.Modal.getInstance(document.getElementById(modalElement.id));
                    bsModal.hide();
                    // Auto-refresh the data table
                    refreshFunction();
                } else {
                    const err = await response.json();
                    showToast(err.detail || "Error occurred", "danger");
                }
            } catch (error) {
                showToast("Connection Error", "danger");
            }
            hideLoader();
        }