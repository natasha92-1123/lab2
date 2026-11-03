---
name: ready-work-item-details
description: Create or maintain GitHub Project backlog and Ready work items with Backlog, User Story, Acceptance Criteria, and Task Cases details.
---

# Backlog and Ready work item details

Use this skill when asked to create a backlog item or inspect and maintain work
items in a GitHub Project's `Ready` column. Every generated or completed issue
body must use the exact section headings `## Backlog`, `## User Story`,
`## Acceptance Criteria`, and `## Task Cases`.

## Mode A: Create a backlog item

Use this mode when the user asks to create, add, or establish a new backlog
item.

1. Identify the current repository:

   ```bash
   gh repo view --json nameWithOwner --jq .nameWithOwner
   ```

2. Convert the user's requested feature into a concise issue title. Preserve
   the user's language and intent; do not add unrelated scope.

3. Generate an issue body with all four sections:

   ```markdown
   ## Backlog
   [高層次功能或工作項目描述]

   ## User Story
   身為 [使用者角色]，我希望 [功能或行為]，以便 [可理解的目的或價值]。

   ## Acceptance Criteria
   - [ ] [可驗證的成功條件]
   - [ ] [可驗證的錯誤或邊界條件]
   - [ ] [必要時的資料、狀態或介面條件]

   ## Task Cases
   - [ ] [分析並確認需求與現有流程]
   - [ ] [實作必要的功能與資料處理]
   - [ ] [補上測試並驗證 Acceptance Criteria]
   ```

4. Create the issue:

   ```bash
   gh issue create --repo <OWNER>/<REPO> --title "<TITLE>" --body "<BODY>"
   ```

5. Locate the project associated with the current repository:

   ```bash
   gh project list --owner <OWNER> --format json
   ```

   Use a project whose items reference the current repository. If the project
   cannot be identified unambiguously, stop after creating the issue and ask
   the user which project to use.

6. Add the new issue to the project and set its status to `Backlog`. Do not
   place a newly created item in `Ready` unless the user explicitly requests
   that status. Use the issue URL returned by `gh issue create`:

   ```bash
   gh project item-add <PROJECT_NUMBER> --owner <OWNER> \
     --url <ISSUE_URL> --format json
   ```

   Then inspect the project fields to find the Status field ID and the
   `Backlog` option ID:

   ```bash
   gh project field-list <PROJECT_NUMBER> --owner <OWNER> --format json
   ```

   Update the newly added item:

   ```bash
   gh project item-edit --id <ITEM_ID> --project-id <PROJECT_ID> \
     --field-id <STATUS_FIELD_ID> \
     --single-select-option-id <BACKLOG_OPTION_ID>
   ```

7. Verify the issue body and project status after creation.

## Mode B: Maintain Ready items

Use this mode when the user asks to inspect, update, or automatically complete
items in the `Ready` column.

1. Identify the repository from the current working directory:

   ```bash
   gh repo view --json nameWithOwner --jq .nameWithOwner
   ```

2. List the owner's open projects and locate the project used by this
   repository:

   ```bash
   gh project list --owner <OWNER> --format json
   ```

   Prefer a project whose items reference the current repository. Do not assume
   a project number if more than one project is available.

3. Inspect the project's items:

   ```bash
   gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json --limit 100
   ```

   Select only items whose `status` is exactly `Ready` and whose content
   belongs to the current repository. Handle issue items; skip draft issues
   and pull requests unless the user explicitly asks for them.

4. For every selected issue, inspect its current body before editing:

   ```bash
   gh issue view <ISSUE_NUMBER> --repo <OWNER>/<REPO> --json title,body
   ```

5. Add content only when the corresponding section is missing:

   - Add a `## Backlog` section that briefly states the feature or work item
     represented by the title.
   - Add a `## User Story` section based on the issue title.
   - Add a `## Acceptance Criteria` section with concrete, testable checklist
     items based on the issue title.
   - Add a `## Task Cases` section describing the implementation tasks needed
     to satisfy the User Story and Acceptance Criteria.
   - Preserve all existing body text and existing sections.
   - If one section already exists, keep its content unchanged and add only the
     other section.
   - Treat headings case-insensitively when checking whether a section exists.

   Use this structure:

   ```markdown
   ## User Story
   身為 [使用者角色]，我希望 [功能或行為]，以便 [可理解的目的或價值]。

   ## Acceptance Criteria
   - [ ] 可驗證的成功條件
   - [ ] 可驗證的錯誤或邊界條件
   - [ ] 必要時的資料、狀態或介面條件

   ## Task Cases
   - [ ] 分析並確認需求與現有流程
   - [ ] 實作必要的功能與資料處理
   - [ ] 補上測試並驗證 Acceptance Criteria
   ```

6. Update each changed issue with `gh issue edit --body`. Do not modify issues
   that already contain all four sections. Do not change project status, labels,
   assignees, milestones, or code.

7. Re-list the project items or fetch the edited issues to verify that every
   Ready issue now has all four headings.

## Writing guidance

- Write in Traditional Chinese when the issue title or repository content is
  Traditional Chinese.
- Treat `Backlog` as the high-level feature statement, not as a project
  status. Do not change the item's Project status.
- Keep the story specific to the title; do not invent unrelated scope.
- Generate all four sections when creating a new backlog item.
- Make acceptance criteria observable and testable.
- Always format every Acceptance Criteria item as an unchecked Markdown
  checklist item beginning with `- [ ]`.
- Do not use ordinary unordered-list markers such as `- ` without `[ ]`.
- Always format every Task Cases item as an unchecked Markdown checklist item
  beginning with `- [ ]`.
- Make Task Cases implementation-oriented and traceable to the acceptance
  criteria.
- Include at least one normal-success criterion and one failure, validation, or
  persistence criterion when applicable.
- Do not claim implementation is complete; this skill only improves work item
  specifications.

## Safety

- Never edit items outside the `Ready` status.
- Never overwrite existing Backlog, User Story, Acceptance Criteria, or Task
  Cases text.
- Preserve the issue body exactly apart from appending the missing sections.
- When creating a backlog item, never silently move it to `Ready`.
- If the target project or repository cannot be identified unambiguously, stop
  and ask for clarification instead of guessing.

## Invocation examples

Create a complete backlog item:

```text
請使用 ready-work-item-details skill 建立 backlog：
新增 BMI 歷史紀錄查詢功能。
建立 issue 後放到 Project 的 Backlog 欄位。
```

Complete existing Ready items:

```text
請使用 ready-work-item-details skill，
檢查 Ready 欄位中的所有 item，補上缺少的
Backlog、User Story、Acceptance Criteria 和 Task Cases。
Acceptance Criteria 和 Task Cases 都要使用 - [ ] checklist 格式。
```
