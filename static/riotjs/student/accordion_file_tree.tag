<accordion-file-tree>
    <div if="{ opts.file.type != 'dir' }" class="title file">
        { file.name }
    </div>

    <div if="{ opts.file.type == 'dir' }" class="title dir">
            <i class="dropdown icon"></i>
            { file.name }
    </div>
    <div if="{ opts.file.type == 'dir' }" class="content">
        <accordion-file-tree each="{ file in file.files }" file="{ file }" class="{ file.type === 'dir' ? "styled accordion" : "" }"></accordion-file-tree>
    </div>

    <style>
        .file {
            color: #333333 !important;
        }

        .dir {
            color: #345fa3 !important;
        }
    </style>
</accordion-file-tree>

