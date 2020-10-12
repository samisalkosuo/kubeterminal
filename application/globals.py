#global constants

#Pod window contents
WINDOW_POD="WINDOW_POD"
WINDOW_SVC="WINDOW_SVC"
WINDOW_CM="WINDOW_CM"
WINDOW_SECRET="WINDOW_SECRET"
WINDOW_SF="WINDOW_SF"
WINDOW_RS="WINDOW_RS"
WINDOW_DS="WINDOW_DS"
WINDOW_PVC="WINDOW_PVC"
WINDOW_PV="WINDOW_PV"
WINDOW_DEPLOYMENT="WINDOW_DEPLOYMENT"
WINDOW_SC="WINDOW_SC"
WINDOW_JOB="WINDOW_JOB"
WINDOW_CRONJOB="WINDOW_CRONJOB"
WINDOW_ROLE="WINDOW_ROLE"
WINDOW_ROLEBINDING="WINDOW_ROLEBINDING"
WINDOW_SA="WINDOW_SA"
WINDOW_PDB="WINDOW_PDB"
WINDOW_ROUTE="WINDOW_ROUTE"
WINDOW_INGRESS="WINDOW_INGRESS"
WINDOW_NODE="WINDOW_NODE"
WINDOW_CRD="WINDOW_CRD"
WINDOW_NAMESPACE="WINDOW_NAMESPACE"

#undocumented
WINDOW_CONTEXT="WINDOW_CONTEXT"

WINDOW_LIST=[WINDOW_POD,
            WINDOW_SVC,
            WINDOW_CM,
            WINDOW_SECRET,
            WINDOW_SF,
            WINDOW_RS,
            WINDOW_DS,
            WINDOW_PVC,
            WINDOW_PV,
            WINDOW_DEPLOYMENT,
            WINDOW_SC,
            WINDOW_JOB,
            WINDOW_CRONJOB,
            WINDOW_ROLE,
            WINDOW_ROLEBINDING,
            WINDOW_SA,
            WINDOW_PDB,
            WINDOW_ROUTE,
            WINDOW_INGRESS,
            WINDOW_NODE,
            WINDOW_CRD,
            WINDOW_NAMESPACE
            ]


WINDOW_COMMAND_WINDOW_TITLE = {
            WINDOW_POD: "POD",#not used
            WINDOW_SVC: "SERVICE",
            WINDOW_CM: "CONFIGMAP",
            WINDOW_SECRET: "SECRET",
            WINDOW_SF: "STATEFULSET",
            WINDOW_RS: "REPLICASET",
            WINDOW_DS: "DAEMONSET",
            WINDOW_PVC: "PERSISTENTVOLUMECLAIM",
            WINDOW_PV: "PERSISTENTVOLUME",
            WINDOW_DEPLOYMENT: "DEPLOYMENT",
            WINDOW_SC: "STORAGECLASS",
            WINDOW_JOB: "JOB",
            WINDOW_CRONJOB: "CRONJOB",
            WINDOW_ROLE: "ROLE",
            WINDOW_ROLEBINDING: "ROLEBINDING",
            WINDOW_SA: "SERVICEACCOUNT",
            WINDOW_PDB: "PODDISRUPTIONBUDGET",
            WINDOW_ROUTE: "ROUTE",
            WINDOW_INGRESS: "INGRESS",
            WINDOW_NODE: "NODE",
            WINDOW_CRD: "CUSTOMRESOURCEDEFINITION",
            WINDOW_NAMESPACE: "NAMESPACE"

}

WINDOW_RESOURCE_TYPE = {
            WINDOW_POD: "pod",
            WINDOW_SVC: "svc",
            WINDOW_CM: "cm",
            WINDOW_SECRET: "secret",
            WINDOW_SF: "sf",
            WINDOW_RS: "rs",
            WINDOW_DS: "ds",
            WINDOW_PVC: "pvc",
            WINDOW_PV: "pv",
            WINDOW_DEPLOYMENT: "deployment",
            WINDOW_SC: "sc",
            WINDOW_JOB: "job",
            WINDOW_CRONJOB: "cronjob",
            WINDOW_ROLE: "role",            
            WINDOW_ROLEBINDING: "rolebinding",
            WINDOW_SA: "sa",
            WINDOW_PDB: "pdb",
            WINDOW_ROUTE: "route",
            WINDOW_INGRESS: "ingress",
            WINDOW_NODE: "node",
            WINDOW_CRD: "crd",
            WINDOW_NAMESPACE: "namespace"

}

#plural
WINDOW_RESOURCES_WINDOW_TITLE = {
            WINDOW_SVC: "Services",
            WINDOW_CM: "ConfigMaps",
            WINDOW_SECRET: "Secrets",
            WINDOW_SF: "StatefulSets",
            WINDOW_RS: "ReplicaSets",
            WINDOW_DS: "DaemonSets",
            WINDOW_PVC: "PersistentVolumeClaims",
            WINDOW_PV: "PersistentVolumes",
            WINDOW_DEPLOYMENT: "Deployments",
            WINDOW_SC: "StorageClasses",
            WINDOW_JOB: "Jobs",
            WINDOW_CRONJOB: "CronJobs",
            WINDOW_ROLE: "Roles",
            WINDOW_ROLEBINDING: "RoleBindings",
            WINDOW_SA: "ServiceAccounts",
            WINDOW_PDB: "PodDisruptionBudgets",
            WINDOW_ROUTE: "Routes",
            WINDOW_INGRESS: "Ingresses",
            WINDOW_NODE: "Nodes",
            WINDOW_CRD: "CustomResourceDefinitions",
            WINDOW_NAMESPACE: "Namespaces"

}
