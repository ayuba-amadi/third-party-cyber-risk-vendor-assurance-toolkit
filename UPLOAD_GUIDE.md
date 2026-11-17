# Uploading subgroup work to GitHub

This public repository is readable by everyone. **A public link does not grant upload rights.** GitHub has no separate permissions for these four folders: repository write access applies across the repository. Do not upload real supplier evidence, credentials, student identifiers or other non-public data; use fictional capstone records only.

## Choose your route

| Your GitHub status | What to do now |
|---|---|
| Accepted collaborator | Upload directly to the correct folder, preferably on a task branch and through a pull request. |
| Invitation pending | Sign in to the **same GitHub account named in the invitation**, open [your repository invitations](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit/invitations), and accept. Refresh the folder page. |
| No invitation or wrong account | Send the team lead your exact GitHub **username and profile URL** in your subgroup chat. Meanwhile use the fork and pull-request route below. |
| No GitHub account yet | Create/sign in to your own GitHub account, share your username/profile URL, then use either route. |

The Academy Outlook address and GitHub account are separate identities. Being in Teams or receiving the project email does not make you a GitHub collaborator.

## A. Direct upload after accepting write access

1. Sign in at GitHub with the account that accepted the invitation.
2. Open the [repository](https://github.com/ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit) and click your subgroup folder:
   - [Research and Risk Assessment](01-research-and-risk-assessment/)
   - [Toolkit Development](02-toolkit-development/)
   - [Testing and Quality Assurance](03-testing-and-quality-assurance/)
   - [Documentation and Presentation](04-documentation-and-presentation/)
3. Inside that folder, choose **Add file → Upload files**. Drag or choose the file. Check that the path at the top starts with your intended folder name.
4. Use a clear commit message such as `research: add questionnaire v1`. Commit to a new task branch when available and open a pull request to `main` for review. If you commit to `main` under the current workflow, report the commit and ask for review immediately.
5. Open the resulting file link and confirm the contents and folder path. Post that link, commit/version and the [submission report](governance/SUBMISSION_RULES.md) in your subgroup chat.

GitHub stores files, not empty folders. Create a new path with a README when the work plan calls for a new directory. Do not replace another member's file without coordinating with its owner.

## B. Contribute now without repository write access

1. While signed in to your GitHub account, open the repository and select **Fork → Create fork**.
2. In your fork, open the matching subgroup folder and choose **Add file → Upload files**. Commit the file in your fork.
3. Select **Contribute → Open pull request** (or **Pull requests → New pull request**) and check that the **base** is `ayuba-amadi/third-party-cyber-risk-vendor-assurance-toolkit:main` and the **head** is your fork/branch.
4. Give the pull request a descriptive title. Include the requirement IDs, file list, checks and gaps from the [submission rules](governance/SUBMISSION_RULES.md). Send its URL to your subgroup and the team lead. The lead reviews and merges it; the file will then appear in this repository.

A pull request is a reviewable submission, not an accepted handoff until the lead reviews it and the relevant files are merged.

## If the button or upload fails

- **No “Add file” on this repository:** check your signed-in GitHub identity and invitation status; use route B while awaiting access.
- **Invitation appears accepted but still read-only:** reload and confirm you used the invited GitHub account. Send your GitHub username and a screenshot of the error to the team lead.
- **Wrong folder:** return to the subgroup folder first, then upload. Check the destination path before committing.
- **File refused:** read GitHub's exact error, check filename and size, and report the error text. Do not place non-public evidence in this public repo or bypass a security warning.
- **PR cannot be opened:** share the URL to the commit in your fork and the exact error in your subgroup chat; a nominated collaborator can assist with the reviewable submission.

**Lead access check:** Repository Settings → Collaborators shows accepted collaborators separately from pending invitations. Invite only the verified GitHub handle supplied by the member. Never infer a GitHub identity solely from an Academy email address. A pending invitation cannot be accepted on the member's behalf.
