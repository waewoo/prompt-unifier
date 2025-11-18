# Feature Description

Multiple Source Repository Support — Allow users to specify multiple source repositories using multiple --repo flags or a list in config.yaml. Enable prompts/rules to be synchronized from multiple Git repositories simultaneously, merge content from all sources into the centralized storage, handle conflicts when multiple repos contain files with same paths, and provide clear feedback about which content came from which repository. Support both CLI (--repo URL1 --repo URL2) and configuration-based (repos: [URL1, URL2] in config.yaml) approaches.
