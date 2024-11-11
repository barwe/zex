K_USER_ID = "userId"  # fm & cm
K_FILE_ID = "fileId"  # cm, also 'id' in fm
K_OVERWRITE = "overwrite"  # 文件已存在时是否覆盖
K_TMPDIR = "TGRPC.TEMP.UPLOADINGS"
K_METASUFFIX = ".meta"
K_EXTRA_NAME = "name"
K_EXTRA_FILE = "file"
K_EXTRA_TMPFILE = "tmp_file"
K_EXTRA_TMPMETAFILE = "tmp_meta_file"
FM_KEYS_HASHED = ("id", "fileSize", "chunked", "chunkSize", "totalChunks", "saveAs", "userId")
FM_KEYS_DUMPED = (*FM_KEYS_HASHED, "overwrite", "extra")
FM_REQUIRED_KEYS = ("id", "fileSize", "chunked", "chunkSIze", "totalChunks", "saveAs", K_USER_ID)
