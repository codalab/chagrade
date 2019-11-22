<accordion-file-tree>
    <div if="{ opts.file.type != 'dir' }" class="title file" data-url="{ opts.file.html_url }">
        <div class="ui radio checkbox">
            <input type="radio" name="html_url">
            <label class="file-label">{ file.name }</label>
        </div>
    </div>

    <div if="{ opts.file.type == 'dir' }" class="title dir" data-url="{ opts.file.html_url }">
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

        .selected-file {
            color: #70c4ff !important;
        }
    </style>
</accordion-file-tree>

