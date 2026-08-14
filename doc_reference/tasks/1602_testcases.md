# Task

Create a [Pipelines] screen. This is the screen at `/qai/v1/projects/:project_id/pipelines`.


At this screen there is a list of the pipelines (test cases) with search bar.
Each pipeline has:
- name
- date created
- code (like TC-001)
- priority
- tags
- the number of steps inside
- status (pending/completed)
- actuality (actual or old and need changes)

# Approximate exampleof page structure
<!DOCTYPE html>

<html class="dark" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>AI QA Agent - Pipeliness</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet"/>
<script>
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#137fec",
                        "background-light": "#f6f7f8",
                        "background-dark": "#101922",
                    },
                    fontFamily: {
                        "display": ["Inter", "sans-serif"]
                    },
                    borderRadius: {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                },
            },
        }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
            font-size: 24px;
        }
    </style>
</head>
<body class="bg-background-light dark:bg-background-dark font-display text-gray-800 dark:text-gray-200">
<div class="flex h-screen">
<!-- SideNavBar -->
<aside class="flex-shrink-0 w-64 bg-white dark:bg-[#111418] border-r border-gray-200 dark:border-gray-800 flex flex-col">
<div class="flex flex-col h-full justify-between p-4">
<div class="flex flex-col gap-4">
<div class="flex items-center gap-3">
<div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10" data-alt="Workspace logo" style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuC8EMYlc6jkKHgglKylIQlOMQFA1Q6iHZ5E2qh2e0aB_Qh32gsD7a3IvzYIDzuJhgxK4p7MAJhzXOktxl_WvqivhSa0eCC7lwe7LtEmKE3lSMcjPKmoMba20X-hmY5OyLos5t4QJec_A8UOKGJwrb40b1jGnr_b_GTlu32iyC5s6pZZYQBT_bKQiJAJ64rVVG2wEZHFQUTr7D_nqxGxRJ-N-uwXpKeBBjvSzLCw3vc_yrDXN9Gp_8G-PPi6Ka2CDOTFlj02qIqE");'></div>
<div class="flex flex-col">
<h1 class="text-gray-900 dark:text-white text-base font-medium leading-normal font-display">AI QA Agent</h1>
<p class="text-gray-500 dark:text-[#9dabb9] text-sm font-normal leading-normal font-display">Workspace</p>
</div>
</div>

</div>

</div>
</aside>
<!-- Main Content -->
<main class="flex-1 flex flex-col overflow-hidden">
<!-- Header -->
<header class="flex-shrink-0 bg-white dark:bg-[#111418] border-b border-gray-200 dark:border-gray-800 p-4">
<div class="flex flex-wrap justify-between items-center gap-3">
<div class="flex flex-col gap-2">
<div class="flex items-center gap-2">
<a class="text-gray-500 dark:text-[#9dabb9] text-sm font-medium leading-normal font-display hover:text-primary dark:hover:text-white" href="#">Project Phoenix</a>
<span class="text-gray-400 dark:text-[#9dabb9] text-sm font-medium leading-normal">/</span>
<span class="text-gray-900 dark:text-white text-sm font-medium leading-normal font-display">Pipeliness</span>
</div>
<h1 class="text-gray-900 dark:text-white text-2xl font-bold leading-tight font-display">Pipeliness</h1>
<p class="text-gray-500 dark:text-[#9dabb9] text-base font-normal leading-normal font-display">Manage and review all test cases for Project Phoenix.</p>
</div>
<button class="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer rounded-lg h-10 px-4 bg-primary text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 transition-colors">
<span class="material-symbols-outlined" style="font-size: 20px;">add_circle</span>
<span class="truncate">New Pipelines</span>
</button>
</div>
</header>
<!-- Two-Panel Layout -->
<div class="flex flex-1 overflow-hidden">
<!-- Left Panel: Pipelines List -->
<div class="w-1/3 max-w-sm flex-shrink-0 border-r border-gray-200 dark:border-gray-800 flex flex-col bg-white dark:bg-[#111418]">
<!-- Search and Filter -->
<div class="p-4 border-b border-gray-200 dark:border-gray-800">
<label class="flex flex-col w-full">
<div class="flex w-full flex-1 items-stretch rounded-lg h-10">
<div class="text-gray-400 dark:text-[#9dabb9] flex bg-gray-100 dark:bg-[#283039] items-center justify-center pl-3 rounded-l-lg">
<span class="material-symbols-outlined" style="font-size: 20px;">search</span>
</div>
<input class="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-r-lg text-gray-800 dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border-none bg-gray-100 dark:bg-[#283039] h-full placeholder:text-gray-400 dark:placeholder:text-[#9dabb9] px-2 text-sm font-normal leading-normal" placeholder="Search by test case title or ID" value=""/>
</div>
</label>
<div class="flex gap-2 pt-3 overflow-x-auto">
<button class="flex h-8 shrink-0 items-center justify-center gap-x-1.5 rounded-lg bg-gray-100 dark:bg-[#283039] px-3">
<p class="text-gray-700 dark:text-white text-sm font-medium leading-normal">Status: All</p>
<span class="material-symbols-outlined text-gray-500 dark:text-white" style="font-size: 20px;">arrow_drop_down</span>
</button>
<button class="flex h-8 shrink-0 items-center justify-center gap-x-1.5 rounded-lg bg-gray-100 dark:bg-[#283039] px-3">
<p class="text-gray-700 dark:text-white text-sm font-medium leading-normal">Priority</p>
<span class="material-symbols-outlined text-gray-500 dark:text-white" style="font-size: 20px;">arrow_drop_down</span>
</button>
<button class="flex h-8 shrink-0 items-center justify-center gap-x-1.5 rounded-lg bg-gray-100 dark:bg-[#283039] px-3">
<p class="text-gray-700 dark:text-white text-sm font-medium leading-normal">Tags</p>
<span class="material-symbols-outlined text-gray-500 dark:text-white" style="font-size: 20px;">arrow_drop_down</span>
</button>
</div>
</div>
<!-- List -->
<div class="flex-1 overflow-y-auto">
<ul class="p-2 space-y-1">
<!-- Selected Item -->
<li>
<a class="block p-3 rounded-lg bg-primary/20 dark:bg-primary/30" href="#">
<div class="flex justify-between items-start">
<p class="text-sm font-semibold text-primary dark:text-white">TC-001: User Login Validation</p>
<div class="w-2.5 h-2.5 rounded-full bg-green-500 mt-1 flex-shrink-0" title="Pass"></div>
</div>
<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
<span>Priority: High</span>
<span>Last Run: 2h ago</span>
</div>
</a>
</li>
<!-- Other Items -->
<li>
<a class="block p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-primary/20 transition-colors" href="#">
<div class="flex justify-between items-start">
<p class="text-sm font-medium text-gray-800 dark:text-gray-200">TC-002: Add Item to Cart</p>
<div class="w-2.5 h-2.5 rounded-full bg-red-500 mt-1 flex-shrink-0" title="Fail"></div>
</div>
<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
<span>Priority: High</span>
<span>Last Run: 3h ago</span>
</div>
</a>
</li>
<li>
<a class="block p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-primary/20 transition-colors" href="#">
<div class="flex justify-between items-start">
<p class="text-sm font-medium text-gray-800 dark:text-gray-200">TC-003: Checkout Process</p>
<div class="w-2.5 h-2.5 rounded-full bg-yellow-500 mt-1 flex-shrink-0" title="Running"></div>
</div>
<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
<span>Priority: Medium</span>
<span>Last Run: 1d ago</span>
</div>
</a>
</li>
<li>
<a class="block p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-primary/20 transition-colors" href="#">
<div class="flex justify-between items-start">
<p class="text-sm font-medium text-gray-800 dark:text-gray-200">TC-004: User Profile Update</p>
<div class="w-2.5 h-2.5 rounded-full bg-gray-400 dark:bg-gray-600 mt-1 flex-shrink-0" title="Not Run"></div>
</div>
<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
<span>Priority: Low</span>
<span>Never</span>
</div>
</a>
</li>
</ul>
</div>
</div>
<!-- Right Panel: Pipelines Details -->
<div class="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark p-6">
<!-- Detail Header -->
<div class="flex flex-wrap justify-between items-center gap-4 mb-6">
<div>
<div class="flex items-center gap-3">
<h2 class="text-2xl font-bold text-gray-900 dark:text-white">TC-001: User Login Validation</h2>
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                                    Pass
                                </span>
</div>
<p class="text-gray-500 dark:text-gray-400 mt-1">Verify that a registered user can successfully log in with valid credentials.</p>
</div>
<div class="flex items-center gap-2">
<button class="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer rounded-lg h-9 px-3 bg-gray-200 dark:bg-[#283039] text-gray-800 dark:text-white text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
<span class="material-symbols-outlined" style="font-size: 18px;">edit</span>
<span>Edit</span>
</button>
<button class="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer rounded-lg h-9 px-3 bg-gray-200 dark:bg-[#283039] text-gray-800 dark:text-white text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
<span class="material-symbols-outlined" style="font-size: 18px;">delete</span>
<span>Delete</span>
</button>
<button class="flex items-center justify-center gap-2 min-w-[84px] cursor-pointer rounded-lg h-9 px-4 bg-primary text-white text-sm font-bold hover:bg-primary/90 transition-colors">
<span class="material-symbols-outlined" style="font-size: 18px;">play_arrow</span>
<span>Run Test</span>
</button>
</div>
</div>
<!-- Tabbed Interface -->
<div>
<div class="border-b border-gray-200 dark:border-gray-700">
<nav aria-label="Tabs" class="-mb-px flex space-x-6">
<a class="whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm text-primary border-primary" href="#">Steps</a>
<a class="whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600" href="#">AI Insights</a>
<a class="whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600" href="#">History</a>
</nav>
</div>
<!-- Tabs Content -->
<div class="py-6">
<!-- Steps Tab Content -->
<div class="overflow-x-auto">
<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
<thead class="bg-gray-50 dark:bg-gray-800">
<tr>
<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-12" scope="col">Step</th>
<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider" scope="col">Action</th>
<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider" scope="col">Expected Result</th>
<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider" scope="col">Actual Result</th>
</tr>
</thead>
<tbody class="bg-white dark:bg-[#111418] divide-y divide-gray-200 dark:divide-gray-700">
<tr>
<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">1</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">Navigate to the login page</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">Login page is displayed</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400 flex items-center gap-2"><span class="material-symbols-outlined text-base">check_circle</span> Passed</td>
</tr>
<tr>
<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">2</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">Enter valid username and password</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">Credentials are entered in the fields</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400 flex items-center gap-2"><span class="material-symbols-outlined text-base">check_circle</span> Passed</td>
</tr>
<tr>
<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">3</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">Click the "Login" button</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">User is redirected to the dashboard</td>
<td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400 flex items-center gap-2"><span class="material-symbols-outlined text-base">check_circle</span> Passed</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
</div>
</div>
</main>
</div>
</body></html>