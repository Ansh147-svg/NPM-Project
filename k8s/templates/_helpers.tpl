{{- define "netvision.backendConfigmap" -}}
{{- tpl (.Files.Get "base/backend-configmap.yaml") . -}}
{{- end -}}

{{- define "netvision.agentConfigmap" -}}
{{- tpl (.Files.Get "base/agent-configmap.yaml") . -}}
{{- end -}}
