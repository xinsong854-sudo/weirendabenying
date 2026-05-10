<template>
  <section v-if="!session.me" class="login-scene login-1999">
    <div class="login-ornament left">1999</div>
    <div class="login-ornament right">FILE</div>
    <div class="login-disclaimer"><span>隐私说明：手机号用于身份验证、安全防护与关联捏Ta已有资产；不会用于营销或分享给第三方，验证码验证完成后即时失效。</span><span aria-hidden="true">隐私说明：手机号用于身份验证、安全防护与关联捏Ta已有资产；不会用于营销或分享给第三方，验证码验证完成后即时失效。</span></div>
    <div class="login-stage-copy">
      <span>REVERSE ARCHIVE / 1999</span>
      <h1>伪人大本营</h1>
      <p>和我们一起，成为入吧</p>
      <div class="stage-rule"><i></i><b>THE PSEUDO HUMAN DOSSIER</b><i></i></div>
    </div>
    <div class="login-card labyrinth-window login-card-refined">
      <div class="window-title">IDENTITY RITUAL</div>
      <div class="login-file-tab"><span>ACCESS FILE</span><b>404</b></div>
      <h1>捏Ta账号登录</h1>
      <p class="tagline">使用捏Ta官方验证码登录，仅用于确认成员身份</p>
      <details class="login-why">
        <summary>我们为何需要你的手机号？</summary>
        <ul>
          <li><b>身份验证：</b>仅用于验证你是“捏Ta”平台的用户，以关联你的已有资产。</li>
          <li><b>安全防护：</b>防止恶意注册与机器人攻击。</li>
          <li><b>数据保护：</b>你的手机号仅作为登录凭证，我们不会用于营销或分享给第三方。验证码在验证完成后即时失效，不会在当前网站服务器留存。</li>
        </ul>
      </details>
      <div class="field"><span class="prefix">+86</span><input v-model.trim="phone" type="tel" inputmode="numeric" maxlength="11" placeholder="输入捏Ta绑定手机号" autocomplete="tel"></div>
      <div class="field"><input v-model.trim="code" type="text" inputmode="numeric" maxlength="4" placeholder="验证码" autocomplete="one-time-code"><button class="code-btn" :disabled="sending || timer > 0" @click="sendCode">{{ timer > 0 ? `${timer}s` : '获取验证码' }}</button></div>
      <label class="agree"><input v-model="agree" type="checkbox"><span>我已阅读并同意 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/user-agreement.html" target="_blank" rel="noopener noreferrer">用户协议</a> 和 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/privacy-policy.html" target="_blank" rel="noopener noreferrer">隐私政策</a></span></label>
      <button class="submit" :disabled="logging" @click="login">{{ logging ? '登录中...' : '踏入世间' }}</button>
      <div class="msg" :class="messageType">{{ message }}</div>
      <div class="foot">未注册手机号验证后将自动登录 · t.nieta.art/UTLCFvWs</div>
    </div>
  </section>

  <section v-else class="labyrinth-app">
    <div v-if="message" class="global-toast" :class="messageType">{{ message }}</div>
    <div v-if="uploadTasks.length" class="upload-task-panel">
      <div class="upload-task-head"><b>图片上传任务</b><span>{{ uploadInProgress ? '上传中，请勿关闭页面' : '上传完成' }}</span></div>
      <div v-for="task in uploadTasks" :key="task.id" class="upload-task-row" :class="task.status">
        <span>{{ task.name }}</span><em>{{ task.status === 'error' ? task.error : `${Math.round(task.progress)}%` }}</em><i><b :style="{ width: task.progress + '%' }"></b></i>
      </div>
    </div>
    <main class="stage-main">
      <Transition name="page-shift">
      <section v-if="view === 'forum'" key="forum" class="forum-theater chat-forum">
        <div class="chat-shell" :class="{ 'member-mode': selectedForum === '成员' }">
          <aside class="chat-sidebar game-channel-sidebar">
            <div class="game-rail">
              <div class="rail-logo">伪</div>
              <button v-for="group in forumGroups" :key="group.name" class="rail-btn" :class="{ active: group.name === selectedForumGroup }" :title="group.name" @click="selectForumGroup(group)"><span>{{ group.icon }}</span><b>{{ group.short || group.name }}</b></button>
            </div>
            <div class="sub-channel-panel" v-if="selectedForumGroup !== '成员'">
              <div class="chat-brand"><span>FORUM</span><b>{{ selectedForumGroup }}</b><small>{{ currentForumGroup?.desc }}</small></div>
              <button v-for="item in currentForumGroup?.items || []" :key="item.name" class="channel-row" :class="{ active: item.name === selectedForum, custom: item.custom }" :title="item.name" @click="selectedForum = item.name; loadForumPosts()"><span>{{ item.code }}</span><b>{{ item.short || item.name }}</b><i v-if="isAdmin && item.custom" class="branch-delete" title="删除分支" @click.stop="deleteForumBranch(item)">×</i></button>
              <button v-if="isAdmin && selectedForumGroup === '地区分支'" class="channel-row create-branch-row" @click="createForumBranch"><span>＋</span><b>开新分支</b></button>
            </div>
          </aside>
          <section class="chat-room">
            <header class="chat-room-head">
              <div><span class="ritual-label">CURRENT CHANNEL</span><h1>{{ selectedForum }}</h1><p>{{ selectedForumDescription }}</p></div>
              <button v-if="false" class="back-note">＋ 发帖</button>
            </header>
            <div v-if="selectedForum === '成员'" class="member-board friend-list-board" :class="{ 'private-open': selectedMember && selectedMemberTool === '私聊' }">
              <aside class="friend-list-pane">
                <div class="member-board-head"><h2>成员</h2><input v-model.trim="memberQuery" type="search" placeholder="搜索成员昵称或称号..."></div>
                <div class="friend-list">
                  <button v-for="m in filteredMembers" :key="m.uuid" class="friend-row" :class="{ online: m.online, active: selectedMember?.uuid === m.uuid }" @click="selectMember(m)">
                    <span class="friend-avatar" @click.stop.prevent="openMemberModal(m)"><span class="framed-avatar" :class="avatarFrameClassFor(m)"><img class="avatar-base" v-if="safeUrl(m.avatar)" :src="safeUrl(m.avatar)" alt="" loading="lazy" referrerpolicy="no-referrer"><b v-else>{{ initials(m.name) }}</b><img v-if="avatarFrameFor(m)?.type === 'frame'" class="avatar-frame" :src="avatarFrameFor(m).url" alt=""><span v-if="avatarFrameFor(m)?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="avatarFrameFor(m).url" alt=""></span></span></span>
                    <span><b>{{ m.name }} <i v-if="['chief','deputy','admin'].includes(m.role)" class="verify-v">V</i></b><small v-if="memberTitle(m)">{{ memberTitle(m) }}</small></span>
                    <em>{{ m.online ? '在线' : timeAgo(m.last_seen) }}</em>
                  </button>
                </div>
              </aside>
              <section v-if="selectedMember" class="friend-detail-pane">
                  <header class="friend-detail-head"><button class="detail-avatar" @click.stop.prevent="openMemberModal(selectedMember)"><span class="framed-avatar" :class="avatarFrameClassFor(selectedMember)"><img class="avatar-base" v-if="safeUrl(selectedMember.avatar)" :src="safeUrl(selectedMember.avatar)" alt="" referrerpolicy="no-referrer"><b v-else>{{ initials(selectedMember.name) }}</b><img v-if="avatarFrameFor(selectedMember)?.type === 'frame'" class="avatar-frame" :src="avatarFrameFor(selectedMember).url" alt=""><span v-if="avatarFrameFor(selectedMember)?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="avatarFrameFor(selectedMember).url" alt=""></span></span></button><div><h2>{{ selectedMember.name }} <span v-if="profileBadge(selectedMember.role)" class="profile-role-badge">{{ profileBadge(selectedMember.role) }}</span><span v-if="['chief','deputy','admin'].includes(selectedMember.role)" class="verify-v">V</span></h2><p v-if="memberTitle(selectedMember)" class="pop-title-badge">{{ memberTitle(selectedMember) }}</p><small>{{ selectedMember.online ? '在线' : timeAgo(selectedMember.last_seen) }}</small><blockquote v-if="selectedMember.signature" class="pop-signature">{{ selectedMember.signature }}</blockquote></div><div class="detail-actions"><button class="title-auth-btn" @click="openPrivatePane(selectedMember)">私聊</button><button v-if="isAdmin" class="title-auth-btn" @click="authorizeTitle(selectedMember)">授权称号</button></div></header>
              </section>
              <section v-if="selectedMember && selectedMemberTool === '私聊'" class="private-side-pane private-drawer">
                <header><b>私聊 · {{ selectedMember.name }}</b><button @click="selectedMemberTool = '资料'">收起</button></header>
                <div class="private-thread private-thread-log"></div>
                <div class="private-compose"><input v-model.trim="privateText" type="text" :placeholder="`私聊 ${selectedMember.name}...`" @keydown.enter="sendPrivateMessage"><button :disabled="!privateText" @click="sendPrivateMessage">发送</button></div>
              </section>
            </div>
            <div v-else-if="selectedForum === '活动颁布'" class="activity-board">
              <section><div class="activity-head"><h2>当前活动</h2><button v-if="isAdmin" class="back-note" @click="createActivity">＋ 新增活动</button></div><article v-for="event in currentActivities" :key="event.title" class="activity-card"><b>{{ event.title }}</b><span>{{ event.status }}</span><p>{{ event.desc }}</p><button v-if="isAdmin && event.custom" class="activity-delete" @click="deleteActivity(event)">删除活动</button></article></section>
              <section><h2>往期活动</h2><article v-for="event in pastActivities" :key="event.title" class="activity-card past"><b>{{ event.title }}</b><span>{{ event.status }}</span><p>{{ event.desc }}</p></article></section>
            </div>
            <div v-else class="thread-list">
              <div v-if="forumLoading" class="item muted">正在同步论坛消息...</div>
              <article v-for="thread in visibleThreads" :key="thread.id" class="thread-message" :class="{ own: thread.user_uuid === session.me?.uuid }">
                <button class="forum-avatar" @click="openForumUser(thread)"><span class="framed-avatar" :class="avatarFrameClassFor(thread)"><img class="avatar-base" v-if="safeUrl(thread.user_avatar)" :src="safeUrl(thread.user_avatar)" alt="" loading="lazy" referrerpolicy="no-referrer"><b v-else>{{ initials(thread.user_name) }}</b><img v-if="avatarFrameFor(thread)?.type === 'frame'" class="avatar-frame" :src="avatarFrameFor(thread).url" alt=""><span v-if="avatarFrameFor(thread)?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="avatarFrameFor(thread).url" alt=""></span></span></button>
                <div class="message-bubble">
                  <header><b>{{ thread.user_name }}</b><time>{{ timeAgo(thread.created_at) }}</time><button v-if="isAdmin" class="danger-mini revoke-inline" @click="revokeThread(thread.id)">撤销</button></header>
                  <p v-if="thread.content">{{ thread.content }}</p>
                  <div v-if="thread.images?.length" class="message-images"><img v-for="img in thread.images" :key="img" :src="img" alt="" loading="lazy"></div>
                </div>
              </article>
              <div v-if="!forumLoading && visibleThreads.length === 0" class="item muted">这个频道还没有发言，来发第一条吧。</div>
            </div>
            <div v-if="!['活动颁布','成员'].includes(selectedForum) && uploadedForumImages.length" class="upload-preview"><span v-for="img in uploadedForumImages" :key="img"><img :src="img" alt=""><button @click="removeUploadedImage(uploadedForumImages, img)">×</button></span></div>
            <div v-if="!['活动颁布','成员'].includes(selectedForum) && imageLibrary.length" class="local-image-library"><b>本地图片库</b><button v-for="item in imageLibrary.slice(0, 12)" :key="item.url" @click="useLibraryImage(uploadedForumImages, item.url)"><img :src="item.url" alt=""><span>使用</span></button></div>
            <div v-if="!['活动颁布','成员'].includes(selectedForum)" class="chat-compose">
              <img :src="safeUrl(session.me.avatar_url)" alt="">
              <input v-model.trim="forumText" type="text" :placeholder="`在「${selectedForum}」发布讨论...`" @keydown.enter="postForumMessage">
              <input ref="forumUploadInput" class="hidden-file" type="file" accept="image/*" multiple @change="onForumImages">
              <button @click="forumUploadInput?.click()">图片</button>
              <button :disabled="forumPosting || (!forumText && !uploadedForumImages.length)" @click="postForumMessage">{{ forumPosting ? '发送中' : '发送' }}</button>
            </div>
          </section>
          <aside class="chat-info">
            <section class="info-card"><h3>频道信息</h3><p>{{ selectedForumDescription }}</p></section>
            <section class="info-card live-user-card"><h3>实时登录用户</h3><b>{{ liveUserCount }}</b><p>当前在线假人数量正在同步中。</p></section>
          </aside>
        </div>
      </section>

      <section v-else-if="view === 'archive'" key="archive" class="archive-theater">
        <div class="page-actions"><button class="back-note primary" @click="openForum">← 返回论坛</button></div>
        <header class="archive-marquee wiki-marquee">
          <div>
            <span class="ritual-label">WIKI INDEX / INTERNAL LEXICON</span>
            <h1>Wiki</h1>
            <p>先选择大类和子目录，再在对应栏目内提交新增、修订或开新栏目申请。</p>
          </div>
        </header>
        <div class="wiki-hierarchy" :class="{ 'is-root': !selectedWikiGroup }">
          <section v-if="!selectedWikiGroup" class="wiki-drill-panel wiki-root-panel">
            <header class="drill-head"><div><span class="ritual-label">SELECT ARCHIVE VOLUME</span><h2>选择档案卷宗</h2><p>Wiki 首页只保留两个主入口。进入后会切换到下一层页面，不再显示另一个主栏目。</p></div></header>
            <div class="drill-grid wiki-root-grid">
              <button v-for="group in wikiGroups" :key="group.name" @click="enterWikiGroup(group.name)"><b>{{ group.short }}</b><small>{{ group.desc }}</small><i>进入卷宗</i></button>
            </div>
          </section>

          <section v-else-if="selectedWikiGroup === '世界信息'" class="wiki-drill-panel">
            <header class="drill-head"><div><span class="ritual-label">WORLD INFORMATION</span><h2>世界信息</h2><p v-if="!selectedWikiSubsection">选择一个子栏目进入下一层。</p><p v-else-if="!selectedWikiCategory">{{ currentWikiSubsection?.desc }}</p><p v-else>当前栏目：{{ selectedWikiCategory }}</p></div><button class="back-note" @click="leaveWikiLevel">返回上一级</button></header>
            <div v-if="!selectedWikiSubsection" class="drill-grid level-one">
              <button v-for="sec in wikiSubsections" :key="sec.name" @click="selectedWikiSubsection = sec.name; selectedWikiCategory = ''; wikiSubmitOpen = false"><b>{{ sec.name }}</b><small>{{ sec.desc }}</small><i>{{ sec.categories.length }} 个子栏目</i></button>
            </div>
            <div v-else-if="!selectedWikiCategory" class="drill-level level-two standalone">
              <header><span>子栏目 / {{ currentWikiSubsection.name }}</span><p>选择更小栏目进入词条页。</p></header>
              <div class="drill-grid compact">
                <button v-for="cat in currentWikiCategories" :key="cat.name" @click="selectedWikiCategory = cat.name; wikiSubmitOpen = false"><b>{{ cat.name }}</b><small>{{ cat.count }} 条 · {{ cat.preview }}</small></button>
              </div>
            </div>
            <div v-else class="drill-level level-three standalone">
              <header><div><span>栏目 / {{ selectedWikiCategory }}</span><h3>{{ selectedWikiCategory }}</h3></div><div class="wiki-actions inline"><button class="back-note" @click="openCategory(selectedWikiCategory)">查看全部词条</button><button class="back-note primary" @click="openWikiEditor('新增词条')">改 Wiki / 新增词条</button></div></header>
              <div v-if="wikiSubmitOpen" class="wiki-submit-panel wiki-editor-panel">
                <div class="wiki-editor-title"><b>Wiki 编辑申请</b><p>审核通过后会直接写入 Wiki；如果分类名与已有分类一致，会自动合并到原分类。</p></div>
                <div class="wiki-form-grid">
                  <label>编辑类型<select v-model="wikiSubmitType"><option value="新增词条">新增词条</option><option value="修订词条">修订词条</option><option value="新建分类">新建分类</option></select></label>
                  <label>大分类 / 归属<select v-model="wikiSubmitGroup"><option value="世界信息">世界信息</option><option value="伪物档案">伪物档案</option></select></label>
                  <label>分类名称<input v-model.trim="wikiSubmitCategory" list="wiki-category-list" placeholder="选择或输入分类名，例如：世界观"><datalist id="wiki-category-list"><option v-for="name in wikiSubmissionTargets" :key="name" :value="name"></option></datalist></label>
                  <label v-if="wikiSubmitType !== '新建分类'">条目名称<input v-model.trim="wikiSubmitEntryName" placeholder="要增加或修订的条目名"></label>
                </div>
                <label class="wiki-content-label">正文内容<textarea v-model.trim="wikiSubmitContent" rows="6" placeholder="写条目正文、修订内容、设定说明等。照片可在下方一起上传，不需要单独开上传入口。"></textarea></label>
                <div class="wiki-photo-row"><input ref="wikiUploadInput" class="hidden-file" type="file" accept="image/*" multiple @change="onWikiImages"><button class="back-note" @click="wikiUploadInput?.click()">添加照片</button><span>{{ uploadedWikiImages.length ? `已添加 ${uploadedWikiImages.length} 张照片` : '可选：上传条目配图 / 证明图' }}</span></div>
                <div v-if="imageLibrary.length" class="local-image-library wiki-library"><b>本地图片库</b><button v-for="item in imageLibrary.slice(0, 12)" :key="item.url" @click="useLibraryImage(uploadedWikiImages, item.url)"><img :src="item.url" alt=""><span>使用</span></button></div>
                <div v-if="uploadedWikiImages.length" class="upload-preview wiki-preview"><span v-for="img in uploadedWikiImages" :key="img"><img :src="img" alt=""><button @click="removeUploadedImage(uploadedWikiImages, img)">×</button></span></div>
                <button class="back-note primary" :disabled="!canSubmitWiki" @click="submitWikiChange">提交给管理员审核</button>
              </div>
              <div class="wiki-entry-preview"><button v-for="entry in currentWikiCategoryPreview.slice(0, 12)" :key="entry.uuid" @click="openEntry(entry.uuid)">{{ entry.name }}</button></div>
            </div>
          </section>

          <section v-else-if="selectedWikiGroup === '伪物档案'" class="wiki-drill-panel artifact-drill">
            <header class="drill-head artifact"><div><span class="ritual-label">PSEUDO-ARTIFACTS ARCHIVE</span><h2>伪物档案</h2><p v-if="!selectedArtifactCategory">选择伪物档案下的子栏目。</p><p v-else>当前子栏目：{{ selectedArtifactCategory }}</p></div><button class="back-note" @click="leaveWikiLevel">返回上一级</button></header>
            <div v-if="!selectedArtifactCategory" class="drill-grid level-one">
              <button v-for="cat in artifactCategories" :key="cat.name" @click="selectedArtifactCategory = cat.name"><b>{{ cat.name }}</b><small>{{ cat.count }} 件记录</small><i>进入子栏目</i></button>
              <button class="artifact-add" @click="openArtifactEditor"><b>改 Wiki / 新增图鉴</b><small>选择分类、条目和照片，提交管理员审核。</small><i>EDIT</i></button>
            </div>
            <main v-else class="artifact-files standalone">
              <div class="artifact-warning"><b>内部图鉴 / {{ selectedArtifactCategory }}</b><span>伪物资料需管理员审核后公开</span><button class="back-note primary" @click="openWikiEditor('新增词条', selectedArtifactCategory, '伪物档案')">改 Wiki / 新增条目</button></div>
              <div v-if="wikiSubmitOpen" class="wiki-submit-panel wiki-editor-panel artifact-editor-panel">
                <div class="wiki-editor-title"><b>Wiki 编辑申请</b><p>审核通过后会直接写入伪物档案；同名分类会合并。</p></div>
                <div class="wiki-form-grid">
                  <label>编辑类型<select v-model="wikiSubmitType"><option value="新增词条">新增词条</option><option value="修订词条">修订词条</option><option value="新建分类">新建分类</option></select></label>
                  <label>大分类 / 归属<select v-model="wikiSubmitGroup"><option value="世界信息">世界信息</option><option value="伪物档案">伪物档案</option></select></label>
                  <label>分类名称<input v-model.trim="wikiSubmitCategory" list="wiki-category-list-artifact" placeholder="选择或输入分类名"><datalist id="wiki-category-list-artifact"><option v-for="name in wikiSubmissionTargets" :key="name" :value="name"></option></datalist></label>
                  <label v-if="wikiSubmitType !== '新建分类'">条目名称<input v-model.trim="wikiSubmitEntryName" placeholder="要增加或修订的条目名"></label>
                </div>
                <label class="wiki-content-label">正文内容<textarea v-model.trim="wikiSubmitContent" rows="6" placeholder="写条目正文、修订内容、设定说明等。照片可在下方一起上传。"></textarea></label>
                <div class="wiki-photo-row"><input ref="wikiUploadInput" class="hidden-file" type="file" accept="image/*" multiple @change="onWikiImages"><button class="back-note" @click="wikiUploadInput?.click()">添加照片</button><span>{{ uploadedWikiImages.length ? `已添加 ${uploadedWikiImages.length} 张照片` : '可选：上传条目配图 / 证明图' }}</span></div>
                <div v-if="imageLibrary.length" class="local-image-library wiki-library"><b>本地图片库</b><button v-for="item in imageLibrary.slice(0, 12)" :key="item.url" @click="useLibraryImage(uploadedWikiImages, item.url)"><img :src="item.url" alt=""><span>使用</span></button></div>
                <div v-if="uploadedWikiImages.length" class="upload-preview wiki-preview"><span v-for="img in uploadedWikiImages" :key="img"><img :src="img" alt=""><button @click="removeUploadedImage(uploadedWikiImages, img)">×</button></span></div>
                <button class="back-note primary" :disabled="!canSubmitWiki" @click="submitWikiChange">提交给管理员审核</button>
              </div>
              <article v-for="entry in artifactEntries" :key="entry.uuid" class="artifact-file" @click="openEntry(entry.uuid)"><div class="artifact-no">{{ entry.name.slice(0, 2) }}</div><div><h3>{{ entry.name }}</h3><p>{{ entry.description }}</p><small>ARCHIVE / {{ selectedArtifactCategory }}</small></div></article>
              <div v-if="!artifactEntries.length" class="wiki-empty-tip">暂无伪物记录。</div>
            </main>
          </section>
        </div>
      </section>

      <section v-else-if="view === 'explore'" key="explore" class="forum-theater">
        <div class="page-actions"><button class="back-note primary" @click="openForum">← 返回论坛</button></div>
        <header class="archive-marquee">
          <div>
            <span class="ritual-label">INNER WORLD / EXPEDITION</span>
            <h1>里界探索</h1>
            <p>探索任务、异常坐标与调查报告入口。完整功能稍后开放。</p>
          </div>
        </header>
        <div class="column-grid">
          <article class="column-card"><h3>异常坐标</h3><p>记录里界地点、路线与危险等级。</p><small>待开放</small></article>
          <article class="column-card"><h3>调查队</h3><p>组织成员探索小队，登记参与者与携带物资。</p><small>待开放</small></article>
          <article class="column-card"><h3>报告归档</h3><p>探索结束后提交报告，管理员审核后并入 Wiki。</p><small>待开放</small></article>
        </div>
      </section>

      <section v-else-if="view === 'category'" key="category" class="category-theater">
        <div class="page-actions"><button class="back-note primary" @click="openForum">← 返回论坛</button><button class="back-note" @click="openArchive">返回 Wiki</button></div>
        <div class="search-bar"><span class="sicon">⌕</span><input v-model.trim="catQuery" type="search" placeholder="在当前分类中搜索..." autocomplete="off"></div>
        <article v-for="e in categoryEntries" :key="e.uuid" class="entry-note" role="button" tabindex="0" @click="openEntry(e.uuid)" @keydown.enter="openEntry(e.uuid)">
          <span v-if="badgeMark(e.description)" class="badge" :class="badgeClass(e.description)">{{ badgeMark(e.description) }}</span>
          <h2>{{ e.name }}</h2>
          <p>{{ e.description }}</p>
          <footer>COMMENT LOG / {{ commentCounts[e.uuid] || 0 }}</footer>
        </article>
      </section>

      <section v-else-if="view === 'entry' && currentEntry" key="entry" class="entry-theater">
        <div class="page-actions"><button class="back-note primary" @click="openForum">← 返回论坛</button><button class="back-note" @click="openCategory(currentEntry.category)">返回 {{ currentEntry.category }}</button></div>
        <article class="entry-full">
          <span v-if="badgeMark(currentEntry.description)" class="badge" :class="badgeClass(currentEntry.description)">{{ badgeMark(currentEntry.description) }}</span>
          <h1>{{ currentEntry.name }}</h1>
          <p>{{ currentEntry.description }}</p>
        </article>
        <section class="comment-stage">
          <h3>档案评论</h3>
          <article v-for="c in comments" :key="`${c.created_at}-${c.user_name}-${c.content}`" class="comment">
            <img :src="safeUrl(c.user_avatar)" alt="" loading="lazy" referrerpolicy="no-referrer">
            <div><b>{{ c.user_name }}</b><time>{{ timeAgo(c.created_at) }}</time><p>{{ c.content }}</p></div>
          </article>
          <div class="comment-form"><img :src="safeUrl(session.me.avatar_url)" alt="" loading="lazy"><textarea v-model.trim="commentText" maxlength="2000" placeholder="写下你的评论..." rows="2"></textarea><button :disabled="posting || !commentText" @click="postComment">{{ posting ? '发送中...' : '发表' }}</button></div>
        </section>
      </section>

      <section v-else-if="view === 'profile'" key="profile" class="profile-theater">
        <div class="page-actions"><button class="back-note primary" @click="openForum">← 返回论坛</button></div>
        <section class="settings-panel profile-page" aria-label="个人中心">
          <header>
            <div>
              <span>PERSONAL CENTER</span>
              <h2>个人中心</h2>
            </div>
          </header>
          <div class="identity-summary">
            <div class="summary-avatar framed-avatar" :class="avatarFrameClass">
              <img class="avatar-base" :src="safeUrl(session.me.avatar_url)" alt="">
              <img v-if="currentAvatarFrame?.type === 'frame'" class="avatar-frame" :src="currentAvatarFrame.url" alt="">
              <span v-if="currentAvatarFrame?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="currentAvatarFrame.url" alt=""></span>
            </div>
            <div class="identity-summary-main">
              <b>{{ session.me.nick_name || session.me.name }}</b>
              <div class="profile-tags"><b v-if="roleLabel(session.role)">{{ roleLabel(session.role) }}</b><i v-if="memberTitle(currentUserProfile)">{{ memberTitle(currentUserProfile) }}</i></div>
              <button v-if="!signatureEditing" class="summary-signature" @click="signatureEditing = true">{{ signatureText || '点击留下签名。' }}</button>
              <section v-else class="inline-signature-editor">
                <label>个人签名</label>
                <textarea v-model.trim="signatureText" maxlength="50" rows="2" placeholder="写下你的个人签名，50字以内..."></textarea>
                <div class="signature-actions"><small>{{ signatureText.length }}/50</small><div><button class="back-note" @click="signatureEditing = false">取消</button><button class="back-note primary" :disabled="savingSignature" @click="saveSignature">{{ savingSignature ? '保存中...' : '保存' }}</button></div></div>
              </section>
            </div>
            <button class="logout-danger" @click="logout">退出登录</button>
          </div>
          <div class="profile-tabs">
            <button :class="{ active: activeProfilePanel === 'frames' }" @click="activeProfilePanel = 'frames'">头像框</button>
            <button :class="{ active: activeProfilePanel === 'card' }" @click="activeProfilePanel = 'card'">身份卡</button>
            <button v-if="isAdmin" :class="{ active: activeProfilePanel === 'review' }" @click="activeProfilePanel = 'review'">待审核</button>
          </div>
          <div v-if="activeProfilePanel === 'frames'" class="setting-block">
            <h3>头像框权限</h3>
            <p>选择当前身份记录的外显装饰。权限仅保存在本机，不会改动账号资料。</p>
            <div class="frame-grid">
              <button v-for="frame in avatarFrames" :key="frame.id" class="frame-option" :class="{ active: avatarFrame === frame.id }" @click="selectAvatarFrame(frame.id)">
                <span class="frame-preview framed-avatar" :class="[frame.type === 'roach' ? 'has-roach-frame' : '', frame.id === 'moonrise' ? 'avatar-frame-moonrise' : '']">
                  <img class="avatar-base" :src="safeUrl(session.me.avatar_url)" alt="">
                  <img v-if="frame.type === 'frame'" class="avatar-frame" :src="frame.url" alt="">
                  <span v-if="frame.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="frame.url" alt=""></span>
                </span>
                <b>{{ frame.name }}</b>
              </button>
            </div><div class="frame-save-row"><button class="back-note primary" @click="saveAvatarFrame">确定使用头像框</button></div>
          </div>
          <div v-else-if="activeProfilePanel === 'card'" class="setting-block identity-card-block identity-card-open">
            <div class="identity-card-headline">
              <div>
                <span class="ritual-label">IDENTITY CARD</span>
                <h3>身份卡 · CoC 车卡</h3>
                <p>粘贴 Neta 角色分享链接 / UUID / 角色名，系统会读取角色公开资料与图片，并生成可跑团使用的 CoC 7版车卡。</p>
              </div>
            </div>
            <div v-if="identityCards.length" class="identity-card-shelf">
              <button v-for="card in identityCards" :key="card.id" class="saved-card-cover" @click="openIdentityCard(card.id)">
                <img v-if="safeUrl(card.avatar_img)" :src="safeUrl(card.avatar_img)" alt="">
                <span v-else>{{ initials(card.source_name || card.investigator?.name) }}</span>
                <b>{{ card.investigator?.name || card.source_name || '未命名调查员' }}</b>
                <small>HP {{ card.hp_current }}/{{ card.hp_max }}</small>
              </button>
            </div>
            <div v-if="selectedIdentityCardDetail" class="saved-card-detail">
              <header><div><span class="ritual-label">SAVED CARD</span><h4>{{ selectedIdentityCardDetail.card?.investigator?.name || selectedIdentityCardDetail.summary?.source_name }}</h4></div><button class="back-note" @click="selectedIdentityCardDetail = null">收起</button></header>
              <div class="identity-derived compact">
                <span>HP {{ selectedIdentityCardDetail.summary.hp_current }}/{{ selectedIdentityCardDetail.summary.hp_max }}</span>
                <button class="hp-chip" @click="updateIdentityCardHp(-1)">-1 HP</button>
                <button class="hp-chip" @click="updateIdentityCardHp(1)">+1 HP</button>
                <button class="hp-chip danger" @click="updateIdentityCardHp(-999)">撕卡</button>
              </div>
              <div class="dimension-radar-wrap" v-if="selectedIdentityCardDetail.card?.attribute_dimensions">
                <svg class="dimension-radar" viewBox="0 0 120 120" aria-label="多维属性雷达图">
                  <polygon class="radar-ring outer" points="60,14 106,60 60,106 14,60" />
                  <polygon class="radar-ring middle" points="60,30 90,60 60,90 30,60" />
                  <line v-for="axis in dimensionAxes" :key="axis.key" class="radar-axis" x1="60" y1="60" :x2="dimensionAxisPoint(axis.index).x" :y2="dimensionAxisPoint(axis.index).y" />
                  <polygon class="radar-poly" :points="dimensionRadarPoints(selectedIdentityCardDetail.card.attribute_dimensions)" />
                  <circle v-for="axis in dimensionAxes" :key="axis.key + '-dot'" class="radar-dot" :cx="dimensionValuePoint(selectedIdentityCardDetail.card.attribute_dimensions, axis.index, axis.key).x" :cy="dimensionValuePoint(selectedIdentityCardDetail.card.attribute_dimensions, axis.index, axis.key).y" r="2.8" />
                </svg>
                <div class="dimension-legend">
                  <div v-for="axis in dimensionAxes" :key="axis.key"><b>{{ selectedIdentityCardDetail.card.attribute_dimensions[axis.key]?.label || axis.label }}</b><strong>{{ selectedIdentityCardDetail.card.attribute_dimensions[axis.key]?.score || 0 }}</strong><small>{{ (selectedIdentityCardDetail.card.attribute_dimensions[axis.key]?.traits || []).join(' · ') }}</small></div>
                </div>
              </div>
              <button class="back-note danger-soft" @click="deleteIdentityCard(selectedIdentityCardDetail.summary.id)">删除这张卡</button>
            </div>
            <div class="identity-card-form">
              <input v-model.trim="identityCardLink" type="text" placeholder="粘贴 Neta 角色分享链接 / UUID / 角色名" @keydown.enter="generateIdentityCard">
              <button class="back-note primary" :disabled="identityCardLoading || !identityCardLink || identityCards.length >= 3" @click="generateIdentityCard">{{ identityCardLoading ? '生成中...' : identityCards.length >= 3 ? '已达三张上限' : '生成身份卡' }}</button>
            </div>
            <div v-if="identityCardLoading" class="identity-generate-progress">
              <div class="progress-head"><b>{{ identityCardStage }}</b><span>{{ Math.round(identityCardProgress) }}%</span></div>
              <div class="progress-track"><i :style="{ width: identityCardProgress + '%' }"></i></div>
              <p>正在读取角色资料并生成 CoC 车卡，请稍等片刻。</p>
            </div>
            <p v-if="identityCards.length >= 3" class="identity-card-error">每人最多保存三张身份卡，请删除旧卡后再生成。</p>
            <p v-if="identityCardError" class="identity-card-error">{{ identityCardError }}</p>
            <article v-if="identityCardResult" class="generated-identity-card">
              <img v-if="identityCardPortrait" class="identity-card-portrait" :src="safeUrl(identityCardPortrait)" alt="角色图片">
              <div class="identity-card-info">
                <span>INVESTIGATOR</span>
                <h4>{{ identityCardResult.investigator?.name || identityCardResult.source_character?.name || identityCardProfile?.name || '未命名调查员' }}</h4>
                <p>{{ identityCardResult.investigator?.occupation || '未知职业' }} · {{ identityCardResult.investigator?.age || '年龄未知' }} · {{ identityCardResult.investigator?.era || '时代未定' }}</p>
                <p>{{ identityCardResult.portrait?.visual_summary || identityCardProfile?.description || '暂无外观摘要' }}</p>
              </div>
              <div class="identity-attrs">
                <b v-for="(value, key) in identityCardResult.attributes || {}" :key="key"><span>{{ key }}</span>{{ value }}</b>
              </div>
              <div class="identity-derived" v-if="identityCardResult.derived">
                <span>SAN {{ identityCardResult.derived.SAN }}</span>
                <span>HP {{ identityCardResult.derived.HP }}</span>
                <span>MP {{ identityCardResult.derived.MP }}</span>
                <span>MOV {{ identityCardResult.derived.MOV }}</span>
                <span>DB {{ identityCardResult.derived.damage_bonus }}</span>
              </div>
              <div class="identity-skills" v-if="identityCardResult.skills?.length">
                <b v-for="skill in identityCardResult.skills.slice(0, 16)" :key="skill.name">{{ skill.name }} {{ skill.value }}</b>
              </div>
              <div class="dimension-radar-wrap" v-if="identityCardResult.attribute_dimensions">
                <svg class="dimension-radar" viewBox="0 0 120 120" aria-label="多维属性雷达图">
                  <polygon class="radar-ring outer" points="60,14 106,60 60,106 14,60" />
                  <polygon class="radar-ring middle" points="60,30 90,60 60,90 30,60" />
                  <line v-for="axis in dimensionAxes" :key="axis.key" class="radar-axis" x1="60" y1="60" :x2="dimensionAxisPoint(axis.index).x" :y2="dimensionAxisPoint(axis.index).y" />
                  <polygon class="radar-poly" :points="dimensionRadarPoints(identityCardResult.attribute_dimensions)" />
                  <circle v-for="axis in dimensionAxes" :key="axis.key + '-dot'" class="radar-dot" :cx="dimensionValuePoint(identityCardResult.attribute_dimensions, axis.index, axis.key).x" :cy="dimensionValuePoint(identityCardResult.attribute_dimensions, axis.index, axis.key).y" r="2.8" />
                </svg>
                <div class="dimension-legend">
                  <div v-for="axis in dimensionAxes" :key="axis.key"><b>{{ identityCardResult.attribute_dimensions[axis.key]?.label || axis.label }}</b><strong>{{ identityCardResult.attribute_dimensions[axis.key]?.score || 0 }}</strong><small>{{ (identityCardResult.attribute_dimensions[axis.key]?.traits || []).join(' · ') }}</small></div>
                </div>
              </div>
              <div class="generated-card-actions"><span class="auto-save-note">已自动保存到你的身份卡。</span></div>
            </article>
          </div>
          <div v-else-if="isAdmin && activeProfilePanel === 'review'" class="setting-block review-block">
            <h3>Wiki 审核台</h3>
            <p>成员提交的新增词条与修订会出现在这里。审核通过后会直接写入 Wiki。</p>
            <div class="review-tabs">
              <button v-for="tab in wikiReviewTabs" :key="tab.value || 'all'" :class="{ active: wikiReviewStatus === tab.value }" @click="switchWikiReview(tab.value)">{{ tab.label }}</button>
            </div>
            <div v-if="!pendingWiki.length" class="wiki-empty-tip">当前筛选下暂无审核记录。</div>
            <div v-for="item in pendingWiki" :key="item.id" class="review-item" :class="`status-${item.status}`">
              <b>{{ item.entry_name || item.target }}</b><span>{{ item.type }}</span><small>{{ item.author }} · {{ timeAgo(item.time) }} · {{ item.target }}</small><p>{{ item.content }}</p>
              <div v-if="item.images?.length" class="review-images"><img v-for="img in item.images" :key="img" :src="img" alt=""></div>
              <div v-if="item.status !== 'pending'" class="review-result"><b>{{ item.status === 'approved' ? '已通过' : '已驳回' }}</b><small>{{ item.reviewed_by || '管理员' }} · {{ timeAgo(item.reviewed_at) }}</small><p v-if="item.review_note">{{ item.review_note }}</p></div>
              <div v-if="item.status === 'pending'" class="review-actions"><button class="back-note primary" @click="reviewWikiSubmission(item, 'approved')">通过并写入 Wiki</button><button class="back-note" @click="reviewWikiSubmission(item, 'rejected')">驳回</button></div>
            </div>
          </div>
        </section>
      </section>
      </Transition>
    </main>

    <div v-if="selectedMemberModal" class="profile-pop-mask" @click.self="closeMemberModal">
      <section class="profile-pop-card">
        <button class="profile-pop-close" aria-label="关闭" @click="closeMemberModal"></button>
        <div class="profile-pop-top"><span>USER PROFILE</span><i>{{ selectedMemberModal.online ? 'ONLINE' : 'OFFLINE' }}</i></div>
        <div class="profile-pop-avatar framed-avatar" :class="avatarFrameClassFor(selectedMemberModal)"><img v-if="safeUrl(selectedMemberModal.avatar)" class="avatar-base" :src="safeUrl(selectedMemberModal.avatar)" alt="" referrerpolicy="no-referrer"><b v-else>{{ initials(selectedMemberModal.name) }}</b><img v-if="avatarFrameFor(selectedMemberModal)?.type === 'frame'" class="avatar-frame" :src="avatarFrameFor(selectedMemberModal).url" alt=""><span v-if="avatarFrameFor(selectedMemberModal)?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="avatarFrameFor(selectedMemberModal).url" alt=""></span></div>
        <h2>{{ selectedMemberModal.name }} <span v-if="profileBadge(selectedMemberModal.role)" class="profile-role-badge">{{ profileBadge(selectedMemberModal.role) }}</span><span v-if="['chief','deputy','admin'].includes(selectedMemberModal.role)" class="verify-v">V</span></h2>
        <p v-if="memberTitle(selectedMemberModal)" class="pop-title-badge">{{ memberTitle(selectedMemberModal) }}</p>
        <blockquote class="pop-signature"><b>签名</b><span>{{ selectedMemberModal.signature || '这个人还没有留下签名。' }}</span></blockquote>
        <div v-if="selectedMemberCards.length" class="pop-card-list">
          <b>身份卡</b>
          <button v-for="card in selectedMemberCards" :key="card.id" @click="openPublicIdentityCard(card.id)">
            <img v-if="safeUrl(card.avatar_img)" :src="safeUrl(card.avatar_img)" alt="">
            <span>{{ card.investigator?.name || card.source_name || '调查员' }}</span>
          </button>
        </div>
        <details v-if="selectedMemberCardDetail" class="pop-card-detail" open>
          <summary>{{ selectedMemberCardDetail.card?.investigator?.name || selectedMemberCardDetail.summary?.source_name }} 的车卡</summary>
          <div class="dimension-radar-wrap" v-if="selectedMemberCardDetail.card?.attribute_dimensions">
            <svg class="dimension-radar" viewBox="0 0 120 120"><polygon class="radar-ring outer" points="60,14 106,60 60,106 14,60" /><polygon class="radar-ring middle" points="60,30 90,60 60,90 30,60" /><line v-for="axis in dimensionAxes" :key="axis.key" class="radar-axis" x1="60" y1="60" :x2="dimensionAxisPoint(axis.index).x" :y2="dimensionAxisPoint(axis.index).y" /><polygon class="radar-poly" :points="dimensionRadarPoints(selectedMemberCardDetail.card.attribute_dimensions)" /></svg>
            <div class="dimension-legend"><div v-for="axis in dimensionAxes" :key="axis.key"><b>{{ selectedMemberCardDetail.card.attribute_dimensions[axis.key]?.label || axis.label }}</b><strong>{{ selectedMemberCardDetail.card.attribute_dimensions[axis.key]?.score || 0 }}</strong></div></div>
          </div>
        </details>
        <small>{{ selectedMemberModal.online ? '在线' : timeAgo(selectedMemberModal.last_seen) }}</small>
        <button v-if="isAdmin" class="title-auth-btn" @click="authorizeTitle(selectedMemberModal)">授权称号</button>
      </section>
    </div>

    <div v-if="formDialog.open" class="form-dialog-mask" @click.self="cancelFormDialog">
      <section class="form-dialog-card">
        <header><span class="ritual-label">OPERATION PANEL</span><h2>{{ formDialog.title }}</h2><p v-if="formDialog.desc">{{ formDialog.desc }}</p></header>
        <div class="form-dialog-fields">
          <label v-for="field in formDialog.fields" :key="field.name">
            <span>{{ field.label }}</span>
            <textarea v-if="field.type === 'textarea'" v-model.trim="formDialog.values[field.name]" :rows="field.rows || 4" :placeholder="field.placeholder || ''"></textarea>
            <select v-else-if="field.type === 'select'" v-model="formDialog.values[field.name]"><option v-for="opt in field.options || []" :key="opt.value ?? opt" :value="opt.value ?? opt">{{ opt.label ?? opt }}</option></select>
            <input v-else v-model.trim="formDialog.values[field.name]" :placeholder="field.placeholder || ''" :maxlength="field.maxlength || 120">
          </label>
        </div>
        <footer><button class="back-note" @click="cancelFormDialog">{{ formDialog.cancelText }}</button><button class="back-note primary" @click="submitFormDialog">{{ formDialog.confirmText }}</button></footer>
      </section>
    </div>

    <footer class="bottom-dock">
      <button :class="{ active: view === 'forum' }" @click="openForum">论坛</button>
      <button :class="{ active: view === 'archive' || view === 'category' || view === 'entry' }" @click="openArchive">Wiki</button>
      <button :class="{ active: view === 'explore' }" @click="openExplore">里界探索</button>
      <button :class="{ active: view === 'profile' }" @click="openProfile">个人中心</button>
    </footer>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import archiveSeed from './pseudo-human-data.json'

const API = 'https://api.talesofai.cn'
const archive = reactive(JSON.parse(JSON.stringify(archiveSeed)))
const TOKEN_KEY = 'NIETA_ACCESS_TOKEN'
// 隐私约定：Neta 登录 Token 为本地调用凭证，只保存在用户浏览器本地 localStorage。
// 后端请求会临时携带 x-token 用于验证身份/代理 Neta API，但后端不落库存储 Token。
// 后端只保存用户主动同步的站内数据：签名、论坛发言、评论、Wiki 投稿、身份卡/车卡等。
// Forum channels and activities are persisted by backend APIs, not localStorage.
const phone = ref('')
const code = ref('')
const agree = ref(false)
const message = ref('')
const messageType = ref('')
const sending = ref(false)
const logging = ref(false)
const timer = ref(0)
const liveUserCount = ref(37)
let liveUserTimer = null
const view = ref('forum')
const currentCat = ref('')
const currentEntry = ref(null)
const globalQuery = ref('')
const serverResults = ref([])
const searchLoading = ref(false)
const searchSeq = ref(0)
const signatureText = ref('')
const signatureEditing = ref(false)
const savingSignature = ref(false)
const catQuery = ref('')
const members = ref([])
const comments = ref([])
const commentText = ref('')
const posting = ref(false)
const commentCounts = ref({})
const forumText = ref('')
const forumPosts = ref([])
const customForumBranches = ref([])
const customActivities = ref([])
const forumLoading = ref(false)
const forumPosting = ref(false)
const forumSeq = ref(0)
const selectedForum = ref('主论坛')
const selectedForumGroup = ref('主论坛')
const selectedMemberTool = ref('资料')
const memberQuery = ref('')
const selectedMember = ref(null)
const selectedMemberModal = ref(null)
const selectedMemberCards = ref([])
const selectedMemberCardDetail = ref(null)
const privateText = ref('')
const selectedWikiGroup = ref('')
const selectedWikiCategory = ref('')
const selectedWikiSubsection = ref('')
const selectedArtifactCategory = ref('')
const wikiSubmitOpen = ref(false)
const wikiSubmitType = ref('新增词条')
const wikiSubmitGroup = ref('世界信息')
const wikiSubmitCategory = ref('')
const wikiSubmitEntryName = ref('')
const wikiSubmitContent = ref('')
const activeProfilePanel = ref('frames')
const identityCardLink = ref('')
const identityCardLoading = ref(false)
const identityCardError = ref('')
const identityCardResult = ref(null)
const identityCardProfile = ref(null)
const identityCardSaving = ref(false)
const identityCardProgress = ref(0)
const identityCardStage = ref('准备生成')
let identityCardProgressTimer = null
const identityCards = ref([])
const selectedIdentityCardDetail = ref(null)
const wikiReviewStatus = ref('pending')
const forumUploadInput = ref(null)
const wikiUploadInput = ref(null)
const uploadedForumImages = ref([])
const uploadedWikiImages = ref([])
const IMAGE_LIBRARY_KEY = 'WEIREN_IMAGE_LIBRARY'
const uploadTasks = ref([])
const imageLibrary = ref(loadImageLibrary())
const uploadInProgress = computed(() => uploadTasks.value.some(t => t.status === 'uploading'))
const savedFrame = localStorage.getItem('NIETA_AVATAR_FRAME')
const avatarFrame = ref(['none', 'roach', 'moonrise'].includes(savedFrame) ? savedFrame : 'roach')
const session = reactive({ me: null, role: 'member', token: '' })
const formDialog = reactive({ open: false, title: '', desc: '', fields: [], values: {}, confirmText: '确认', cancelText: '取消', resolve: null })
const avatarFrames = [
  { id: 'none', name: '无头像框', url: '', type: 'none' },
  { id: 'roach', name: '乱爬蟑螂', url: 'https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/53710f82-1ad8-4863-98ee-4d7bed45f215.png', type: 'roach' },
  { id: 'moonrise', name: '月升', url: 'https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/5e22d7db-3abd-4861-864e-725538d3794b.png', type: 'frame' }
]

const allEntries = computed(() => Object.entries(archive.lore).flatMap(([category, entries]) => entries.map(e => ({ ...e, category }))))
const categoryCards = computed(() => Object.entries(archive.lore).map(([name, list]) => ({
  name,
  count: list.length,
  preview: (list || []).slice(0, 3).map(e => e.name).join(' · ') || '暂无档案'
})).sort((a, b) => b.count - a.count))
const artifactCategoryNames = ['伪物档案']
const worldCategories = computed(() => categoryCards.value.filter(cat => !artifactCategoryNames.includes(cat.name)))
const artifactCategories = computed(() => categoryCards.value.filter(cat => artifactCategoryNames.includes(cat.name)))
const wikiGroups = computed(() => [
  { name: '世界信息', short: '世界信息', desc: '表界、里界、组织、地点、人物与活动。' },
  { name: '伪物档案', short: '伪物档案', desc: '伪物、异常物件与收容记录。' }
])
const wikiSubsections = computed(() => {
  const pick = names => categoryCards.value.filter(c => names.includes(c.name))
  return [
    { name: '世界基础', desc: '基础设定、里界概念、常人视角与规则。', categories: pick(['世界观', 'deus false', '常人视角']) },
    { name: '人物档案', desc: '人类、伪人及相关身份记录。', categories: pick(['人类档案', '伪人档案']) },
    { name: '地区与组织', desc: '表界、里界、哨站、西陆联盟与组织。', categories: pick(['表界', '表界——公寓', '表界——哨站', '西陆联盟派系', '里界']) },
    { name: '公寓登记', desc: '槐安、茶居住户登记与楼层信息。', categories: pick(['槐安公寓住户登记表', '茶居寓住户登记表']) },
    { name: '活动与群务', desc: '活动、颁奖、群助手与运营资料。', categories: pick(['活动简介', '活动颁奖', '群助手']) }
  ].filter(s => s.categories.length)
})
const currentWikiSubsection = computed(() => wikiSubsections.value.find(s => s.name === selectedWikiSubsection.value) || null)
const currentWikiCategories = computed(() => currentWikiSubsection.value?.categories || [])
const wikiSubmissionTargets = computed(() => archiveCategoriesList.value)
const archiveCategoriesList = computed(() => categoryCards.value.map(c => c.name))
const currentWikiCategoryPreview = computed(() => (archive.lore[selectedWikiCategory.value] || []))
const canSubmitWiki = computed(() => !!wikiSubmitCategory.value.trim() && !!wikiSubmitContent.value.trim() && (wikiSubmitType.value === '新建分类' || !!wikiSubmitEntryName.value.trim()))
const artifactEntries = computed(() => archive.lore[selectedArtifactCategory.value] || [])
const isAdmin = computed(() => ['chief', 'deputy', 'admin'].includes(session.role))
const forumBranches = [
  { code: 'MAIN', name: '主论坛', desc: '公告、规则与日常讨论。' },
  { code: 'YUAN', name: '渊', desc: '渊地区、城市、国家与本地传闻。' },
  { code: 'WEST', name: '西陆', desc: '西陆联盟、派系、边境与圣使教相关讨论。' },
  { code: 'RED', name: '赤星', desc: '赤星地区记录、异常事件与地区角色。' },
  { code: 'ABYSS', name: '里界', desc: '里界地点、异常坐标与探索报告。' },
  { code: 'SURF', name: '表界', desc: '表界资料、组织与常人视角内容。' },
  { code: 'HUAI', name: '槐安公寓', desc: '槐安公寓住户、楼层与事件讨论。' },
  { code: 'TEA', name: '茶居公寓', desc: '茶居公寓住户、楼层与事件讨论。' },
  { code: 'OUT', name: '哨站', desc: '哨站、外勤地点与营地外围记录。' },
  { code: 'OTHER', name: '其他地区', desc: '未归档地区、临时地名与待确认资料。' }
]
const forumColumns = [
  { code: 'ABSC', name: '艾尔伯特里界调查委员会（ABSC）', desc: '里界异常事件、调查记录与委员会公告。', note: 'ABSC FILES' },
  { code: 'BNTY', name: '悬赏栏目', desc: '悬赏任务、素材征集、线索交换与完成登记。', note: 'BOUNTY' },
  { code: 'EVT', name: '活动颁布', desc: '活动规则、奖励、时间与投稿入口。管理员可编辑。', note: 'ADMIN EDITABLE' },
  { code: 'AD', name: '广告区', desc: '成员作品、摊位、招募与交换信息张贴处。', note: 'AD BOARD' }
]
const forumGroups = computed(() => [
  { icon: '主', name: '主论坛', desc: '公告、规则、日常聊天与综合讨论。', items: [forumBranches[0], ...forumColumns] },
  { icon: '地', name: '地区分支', desc: '参考伪人大本营地区国家的分支频道。', items: [...forumBranches.slice(1), ...customForumBranches.value] },
  { icon: '员', name: '成员', short: '成员', desc: '查看全部成员、头像、称号与在线状态。', items: [{ code: 'MEM', name: '成员', short: '成员', desc: '查看全部成员、头像、称号与在线状态。' }] }
])
const currentForumGroup = computed(() => forumGroups.value.find(g => g.name === selectedForumGroup.value) || forumGroups.value[0])
const baseActivities = [
  { title: '熙熙攘攘，我们的哨站', status: '进行中', desc: '当前开放的哨站主题活动，成员可提交设定、记录与作品。' }
]
const currentActivities = computed(() => [...customActivities.value, ...baseActivities])
const pastActivities = [
  { title: '槐安身份卡', status: '归档', desc: '身份卡相关活动记录，后续身份卡功能开放后可继续承接。' },
  { title: '一起来交换礼物吧', status: '已颁奖', desc: '礼物交换活动已结束，获奖与参与记录归档。' },
  { title: '真偷只有一个', status: '已颁奖', desc: '往期推理/互动活动，结果已归档。' }
]
const pendingWiki = ref([])
const CACHE_TTL = 30000
const cacheStamp = reactive({ members: 0, forumMeta: 0, wikiArchive: 0, identityCards: 0 })
const forumPostStamp = reactive({})
function cacheFresh(key, ttl = CACHE_TTL) { return Date.now() - (cacheStamp[key] || 0) < ttl }
function forumFresh(channel, ttl = 10000) { return Date.now() - (forumPostStamp[channel] || 0) < ttl }
function markCache(key) { cacheStamp[key] = Date.now() }
function markForum(channel) { forumPostStamp[channel] = Date.now() }
function clearCache(key) { if (key) cacheStamp[key] = 0 }

const wikiReviewTabs = [
  { value: 'pending', label: '待审核' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已驳回' },
  { value: '', label: '全部' }
]
const dimensionAxes = [
  { key: 'physical', label: '身体', index: 0 },
  { key: 'mental', label: '精神', index: 1 },
  { key: 'social', label: '社交', index: 2 },
  { key: 'occult', label: '神秘', index: 3 }
]
function dimensionAxisPoint(index, radius = 46) {
  const angles = [-90, 0, 90, 180]
  const rad = angles[index] * Math.PI / 180
  return { x: 60 + Math.cos(rad) * radius, y: 60 + Math.sin(rad) * radius }
}
function dimensionValuePoint(dimensions = {}, index, key) {
  const raw = Number(dimensions?.[key]?.score || 0)
  const radius = Math.max(0, Math.min(100, raw)) / 100 * 46
  return dimensionAxisPoint(index, radius)
}
function dimensionRadarPoints(dimensions = {}) {
  return dimensionAxes.map(axis => {
    const p = dimensionValuePoint(dimensions, axis.index, axis.key)
    return `${p.x},${p.y}`
  }).join(' ')
}
const wikiReviewCounts = computed(() => wikiReviewTabs.reduce((acc, tab) => {
  acc[tab.value] = tab.value ? pendingWiki.value.filter(x => x.status === tab.value).length : pendingWiki.value.length
  return acc
}, {}))
const selectedForumDescription = computed(() => {
  const branch = [...forumBranches, ...customForumBranches.value].find(x => x.name === selectedForum.value)
  const col = forumColumns.find(x => x.name === selectedForum.value)
  return branch?.desc || col?.desc || '论坛频道'
})
const visibleThreads = computed(() => forumPosts.value.filter(t => !t.revoked))
const globalResults = computed(() => {
  const q = globalQuery.value.trim()
  if (!q) return []
  return serverResults.value.length ? serverResults.value : filterEntries(allEntries.value, q).slice(0, 20)
})
const categoryEntries = computed(() => filterEntries(archive.lore[currentCat.value] || [], catQuery.value))
const sortedMembers = computed(() => [...members.value].sort((a, b) => Number(b.online) - Number(a.online) || (Number(b.last_seen || 0) - Number(a.last_seen || 0))))
const filteredMembers = computed(() => {
  const q = memberQuery.value.toLowerCase()
  return sortedMembers.value.filter(m => !q || `${m.name} ${memberTitle(m)}`.toLowerCase().includes(q))
})
const currentUserProfile = computed(() => members.value.find(m => m.uuid === session.me?.uuid) || { role: session.role, title: '', signature: signatureText.value })
const currentAvatarFrame = computed(() => avatarFrames.find(f => f.id === avatarFrame.value && f.url) || null)
const identityCardPortrait = computed(() => identityCardResult.value?.portrait?.avatar_img || identityCardResult.value?.source_character?.avatar_img || identityCardProfile.value?.avatar_img || identityCardResult.value?.portrait?.header_img || identityCardProfile.value?.header_img || '')
const avatarFrameClass = computed(() => currentAvatarFrame.value ? (currentAvatarFrame.value.type === 'roach' ? 'has-roach-frame avatar-frame-roach' : `avatar-frame-${currentAvatarFrame.value.id}`) : '')
function avatarFrameFor(member) {
  const uid = member?.uuid || member?.user_uuid
  const frameId = uid && uid === session.me?.uuid ? avatarFrame.value : (member?.avatar_frame || 'none')
  return avatarFrames.find(f => f.id === frameId && f.url) || null
}
function avatarFrameClassFor(member) { const f = avatarFrameFor(member); return f ? (f.type === 'roach' ? 'has-roach-frame avatar-frame-roach' : `avatar-frame-${f.id}`) : '' }

function openFormDialog(options) {
  formDialog.title = options.title || '操作'
  formDialog.desc = options.desc || ''
  formDialog.fields = options.fields || []
  formDialog.values = {}
  for (const field of formDialog.fields) formDialog.values[field.name] = field.value ?? ''
  formDialog.confirmText = options.confirmText || '确认'
  formDialog.cancelText = options.cancelText || '取消'
  formDialog.open = true
  return new Promise(resolve => { formDialog.resolve = resolve })
}
function cancelFormDialog() { formDialog.open = false; formDialog.resolve?.(null); formDialog.resolve = null }
function submitFormDialog() { const values = { ...formDialog.values }; formDialog.open = false; formDialog.resolve?.(values); formDialog.resolve = null }
function makeBranchCode(name) { return String(name || 'NEW').trim().replace(/\s+/g, '').slice(0, 4).toUpperCase() || 'NEW' }
async function loadForumMeta(force = false) {
  if (!force && cacheFresh('forumMeta') && customActivities.value.length + customForumBranches.value.length + pendingWiki.value.length > 0) return
  const [channels, acts, wikiRows] = await Promise.all([
    api('/api/forum/channels').catch(() => []),
    api('/api/activities').catch(() => []),
    api(`/api/wiki/submissions?status=${encodeURIComponent(wikiReviewStatus.value)}`).catch(() => [])
  ])
  customForumBranches.value = Array.isArray(channels) ? channels : []
  customActivities.value = Array.isArray(acts) ? acts : []
  pendingWiki.value = Array.isArray(wikiRows) ? wikiRows : []
  markCache('forumMeta')
}
async function createForumBranch() {
  const values = await openFormDialog({ title: '开新地区分支', desc: '创建一个新的地区频道入口。', confirmText: '创建分支', fields: [
    { name: 'name', label: '分支名称', placeholder: '例如：雾港' },
    { name: 'desc', label: '分支说明', type: 'textarea', rows: 3, placeholder: '这个地区分支用于讨论什么？' }
  ] })
  if (!values) return
  const name = values.name?.trim()
  if (!name) return
  const exists = [...forumBranches, ...forumColumns, ...customForumBranches.value].some(x => x.name === name)
  if (exists) { showMsg('这个分支/频道已经存在'); return }
  const desc = values.desc?.trim() || `${name}地区分支讨论区。`
  try {
    await api('/api/forum/channels', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ code: makeBranchCode(name), name, desc }) })
    await loadForumMeta(true)
    selectedForumGroup.value = '地区分支'; selectedForum.value = name.slice(0, 30); await loadForumPosts(true); showMsg('新分支已创建', 'ok')
  } catch (e) { showMsg(`创建失败：${e.message}`) }
}
async function deleteForumBranch(item) {
  if (!item?.custom) return
  if (!window.confirm(`删除分支「${item.name}」？\n只会删除分支入口，不会删除该频道历史发言。`)) return
  try {
    await api('/api/forum/channels/delete', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ name: item.name }) })
    await loadForumMeta(true)
    if (selectedForum.value === item.name) selectedForum.value = forumBranches[1]?.name || '渊'
    await loadForumPosts(true); showMsg('分支入口已删除', 'muted')
  } catch (e) { showMsg(`删除失败：${e.message}`) }
}
async function createActivity() {
  const values = await openFormDialog({ title: '新增活动', desc: '发布一个活动入口，成员会在活动颁布中看到。', confirmText: '新增活动', fields: [
    { name: 'title', label: '活动标题', placeholder: '活动名称' },
    { name: 'status', label: '活动状态', type: 'select', value: '进行中', options: ['进行中', '招募中', '已结束', '归档'] },
    { name: 'desc', label: '活动说明', type: 'textarea', rows: 4, placeholder: '写下活动规则、时间、奖励或投稿方式。' }
  ] })
  if (!values) return
  const title = values.title?.trim()
  if (!title) return
  if (currentActivities.value.some(x => x.title === title)) { showMsg('这个活动已经存在'); return }
  const desc = values.desc?.trim() || '暂无说明。'
  const status = values.status?.trim() || '进行中'
  try {
    await api('/api/activities', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ title, status, desc }) })
    await loadForumMeta(true); showMsg('活动已新增', 'ok')
  } catch (e) { showMsg(`新增活动失败：${e.message}`) }
}
async function deleteActivity(event) {
  if (!event?.custom) return
  if (!window.confirm(`删除活动「${event.title}」？`)) return
  try {
    await api('/api/activities/delete', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ id: event.id }) })
    await loadForumMeta(true); showMsg('活动已删除', 'muted')
  } catch (e) { showMsg(`删除活动失败：${e.message}`) }
}
async function submitWikiChange() {
  if (!canSubmitWiki.value) return
  const category = wikiSubmitCategory.value.trim()
  const entryName = wikiSubmitEntryName.value.trim()
  const payload = { target: category, group: wikiSubmitGroup.value, category, entry_name: entryName, type: wikiSubmitType.value, content: wikiSubmitContent.value, images: uploadedWikiImages.value }
  try {
    await api('/api/wiki/submissions', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify(payload) })
    wikiSubmitContent.value = ''; wikiSubmitEntryName.value = ''; uploadedWikiImages.value = []; wikiSubmitOpen.value = false
    await loadForumMeta(true); showMsg('已提交给管理员审核', 'ok')
  } catch (e) { showMsg(`提交失败：${e.message}`) }
}
function openWikiEditor(type = '新增词条', category = selectedWikiCategory.value, group = selectedWikiGroup.value === '伪物档案' ? '伪物档案' : '世界信息') {
  wikiSubmitType.value = type
  wikiSubmitGroup.value = group
  wikiSubmitCategory.value = category || ''
  wikiSubmitEntryName.value = ''
  wikiSubmitContent.value = ''
  uploadedWikiImages.value = []
  wikiSubmitOpen.value = true
}
function openArtifactEditor() {
  selectedArtifactCategory.value = artifactCategories.value[0]?.name || '伪物档案'
  openWikiEditor('新增词条', selectedArtifactCategory.value, '伪物档案')
}
async function loadWikiArchive(force = false) {
  if (!force && cacheFresh('wikiArchive')) return
  const data = await api('/api/wiki/archive').catch(() => null)
  if (data?.lore) archive.lore = data.lore
  if (data?.stats) archive.stats = data.stats
  markCache('wikiArchive')
}
async function reviewWikiSubmission(item, action) {
  if (!item?.id) return
  const values = await openFormDialog({ title: action === 'approved' ? '通过 Wiki 提交' : '驳回 Wiki 提交', desc: `${item.entry_name || item.target} · ${item.target}`, confirmText: action === 'approved' ? '通过并写入' : '确认驳回', fields: [
    { name: 'note', label: action === 'approved' ? '通过备注' : '驳回原因', type: 'textarea', rows: 3, placeholder: action === 'approved' ? '可留空' : '建议写明需要修改的地方' }
  ] })
  if (!values) return
  try {
    await api('/api/wiki/review', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ id: item.id, action, note: values.note || '' }) })
    await Promise.all([loadWikiArchive(true), loadForumMeta(true)])
    showMsg(action === 'approved' ? '已通过并写入 Wiki' : '已驳回', 'ok')
  } catch (e) { showMsg(`审核失败：${e.message}`) }
}
function switchWikiReview(status) { wikiReviewStatus.value = status; loadForumMeta(true) }
function closeFormDialog() { if (formDialog.open) cancelFormDialog() }
function filterEntries(list, q) {
  const needle = String(q || '').toLowerCase()
  if (!needle) return list
  return list.filter(e => `${e.name}\n${e.description}`.toLowerCase().includes(needle))
}
function vp(p) { return /^1[3456789]\d{9}$/.test(p) }
function roleLabel(role) { return ({ chief: '营长', deputy: '二营长', admin: '管理员' })[role] || '' }
function profileBadge(role) { return roleLabel(role) }
function memberTitle(m) { return (m?.title || '').trim() }
function initials(name = '') { return String(name || '?').trim().slice(0, 1).toUpperCase() || '?' }
function showMsg(text, type = 'error') { message.value = text; messageType.value = type; clearTimeout(showMsg._t); showMsg._t = setTimeout(() => { if (message.value === text) message.value = '' }, type === 'error' ? 3200 : 1500) }
async function saveSignature() {
  try {
    savingSignature.value = true
    const res = await api('/api/members/signature', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ signature: signatureText.value }) })
    signatureText.value = res?.signature || ''
    if (session.me) session.me.signature = signatureText.value
    members.value = members.value.map(m => m.uuid === session.me?.uuid ? { ...m, signature: signatureText.value } : m)
    signatureEditing.value = false
    showMsg('签名已保存', 'ok')
  } catch (e) { showMsg(`保存失败：${e.message}`) } finally { savingSignature.value = false }
}
async function authorizeTitle(member) {
  const values = await openFormDialog({ title: `授权称号 · ${member.name}`, desc: '管理员可直接授予或清除称号。', confirmText: '保存称号', fields: [
    { name: 'title', label: '称号', value: member.title || '', placeholder: '输入称号，留空则清除' }
  ] })
  if (!values) return
  const title = values.title ?? ''
  try {
    await api('/api/members/title', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ uuid: member.uuid, title }) })
    await loadMembers(true)
    showMsg(title ? '称号已授权' : '称号已清除', 'ok')
  } catch (e) { showMsg(`授权失败：${e.message}`) }
}
async function sendPrivateMessage() {
  if (!selectedMember.value || !privateText.value) return
  try {
    await api('/api/private/messages', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ to_uuid: selectedMember.value.uuid, content: privateText.value }) })
    privateText.value = ''
    showMsg('私聊已发送', 'ok')
  } catch (e) { showMsg(`私聊发送失败：${e.message}`) }
}
function selectMember(member) { selectedMember.value = member; selectedMemberTool.value = '资料'; closeMemberModal() }
function openPrivatePane(member) { selectedMember.value = member; selectedMemberTool.value = '私聊'; closeMemberModal() }
async function openMemberModal(member) {
  selectedMember.value = member
  selectedMemberTool.value = '资料'
  selectedMemberModal.value = { ...member }
  selectedMemberCards.value = []
  selectedMemberCardDetail.value = null
  if (member?.uuid) selectedMemberCards.value = await api(`/api/member/identity-cards?uuid=${encodeURIComponent(member.uuid)}`).catch(() => [])
}
function closeMemberModal() { selectedMemberModal.value = null; selectedMemberCards.value = []; selectedMemberCardDetail.value = null }
async function openPublicIdentityCard(id) { selectedMemberCardDetail.value = await api(`/api/member/identity-card?id=${encodeURIComponent(id)}`).catch(() => null) }
function openProfile() { navigate('profile'); loadIdentityCards() }
function startIdentityProgress() {
  clearInterval(identityCardProgressTimer)
  identityCardProgress.value = 5
  identityCardStage.value = '解析角色链接'
  const stages = [
    { at: 18, text: '读取 Neta 角色资料' },
    { at: 38, text: '整理角色设定' },
    { at: 58, text: '生成 CoC 属性' },
    { at: 76, text: '生成技能与背景' },
    { at: 90, text: '校验车卡数据' }
  ]
  identityCardProgressTimer = setInterval(() => {
    const next = Math.min(92, identityCardProgress.value + Math.random() * 6 + 1)
    identityCardProgress.value = next
    const current = stages.slice().reverse().find(s => next >= s.at)
    if (current) identityCardStage.value = current.text
  }, 650)
}
function finishIdentityProgress(success = true) {
  clearInterval(identityCardProgressTimer)
  identityCardProgressTimer = null
  identityCardProgress.value = success ? 100 : 0
  identityCardStage.value = success ? '生成完成' : '生成失败'
}
function resetIdentityDraft() {
  identityCardResult.value = null
  identityCardProfile.value = null
  identityCardError.value = ''
}
async function generateIdentityCard() {
  if (!session.token) { showMsg('请先登录'); return }
  if (!identityCardLink.value) { showMsg('请粘贴角色链接 / UUID / 角色名'); return }
  if (identityCards.value.length >= 3) { showMsg('每人最多保存三张身份卡'); return }
  identityCardLoading.value = true
  resetIdentityDraft()
  startIdentityProgress()
  try {
    const data = await api('/api/coc/character-card', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-token': session.token },
      body: JSON.stringify({ link: identityCardLink.value }),
      timeout: 90000
    })
    identityCardResult.value = data.card
    identityCardProfile.value = data.profile
    finishIdentityProgress(true)
    await loadIdentityCards(true)
    if (data?.saved?.id) await openIdentityCard(data.saved.id)
    showMsg('身份卡已生成并保存', 'ok')
  } catch (e) {
    finishIdentityProgress(false)
    identityCardError.value = e.message
    showMsg(`生成失败：${e.message}`)
  } finally {
    setTimeout(() => { identityCardLoading.value = false }, identityCardResult.value ? 450 : 900)
  }
}
async function loadIdentityCards(force = false) {
  if (!session.token) return
  if (!force && cacheFresh('identityCards') && identityCards.value.length) return
  identityCards.value = await api('/api/identity-cards', { headers: { 'x-token': session.token } }).catch(() => [])
  markCache('identityCards')
}
async function saveGeneratedIdentityCard() {
  if (!identityCardResult.value) return
  identityCardSaving.value = true
  try {
    const data = await api('/api/identity-cards', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ card: identityCardResult.value, profile: identityCardProfile.value }) })
    await loadIdentityCards(true)
    identityCardResult.value = null
    identityCardProfile.value = null
    identityCardLink.value = ''
    showMsg('身份卡已保存', 'ok')
    if (data?.card?.id) await openIdentityCard(data.card.id)
  } catch (e) { showMsg(`保存失败：${e.message}`) } finally { identityCardSaving.value = false }
}
async function openIdentityCard(id) {
  selectedIdentityCardDetail.value = await api(`/api/identity-cards/${id}`, { headers: { 'x-token': session.token } })
}
async function deleteIdentityCard(id) {
  if (!window.confirm('删除这张身份卡？')) return
  await api('/api/identity-cards/delete', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ id }) })
  selectedIdentityCardDetail.value = null
  await loadIdentityCards(true)
  showMsg('身份卡已删除', 'muted')
}
async function updateIdentityCardHp(delta) {
  const detail = selectedIdentityCardDetail.value
  if (!detail) return
  const next = Math.max(0, Number(detail.summary.hp_current || 0) + delta)
  const res = await api('/api/identity-cards/state', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ id: detail.summary.id, hp_current: next }) })
  if (res.status === 'torn') {
    selectedIdentityCardDetail.value = null
    await loadIdentityCards(true)
    showMsg('生命值归零，已自动撕卡')
    return
  }
  await openIdentityCard(detail.summary.id)
  await loadIdentityCards(true)
}
function selectForumGroup(group) { selectedForumGroup.value = group.name; selectedForum.value = group.items?.[0]?.name || selectedForum.value; loadForumPosts() }
async function revokeThread(id) { try { await api('/api/forum/revoke', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ id }) }); await loadForumPosts(true); showMsg('已撤销发言', 'muted') } catch (e) { showMsg(`撤销失败：${e.message}`) } }
function selectAvatarFrame(id) { avatarFrame.value = id; showMsg('已选择头像框，点击确定后保存', 'muted') }
async function saveAvatarFrame() { const id = avatarFrame.value; localStorage.setItem('NIETA_AVATAR_FRAME', id); try { await api('/api/members/avatar-frame', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ avatar_frame: id }) }); members.value = members.value.map(m => m.uuid === session.me?.uuid ? { ...m, avatar_frame: id } : m); if (selectedMember.value?.uuid === session.me?.uuid) selectedMember.value = { ...selectedMember.value, avatar_frame: id }; if (selectedMemberModal.value?.uuid === session.me?.uuid) selectedMemberModal.value = { ...selectedMemberModal.value, avatar_frame: id }; await loadMembers(true); await loadForumPosts(true) } catch (e) { showMsg(`头像框保存失败：${e.message}`); return } showMsg(id === 'none' ? '已取消头像框' : '头像框已保存', 'ok') }
function openForumUser(thread) { const m = members.value.find(x => x.uuid === thread.user_uuid) || { uuid: thread.user_uuid, name: thread.user_name, avatar: thread.user_avatar, avatar_frame: thread.avatar_frame || 'none', online: false, last_seen: thread.created_at }; openMemberModal(m) }
function safeUrl(url) { const s = String(url || '').trim(); return /^(https?:)?\/\//i.test(s) ? s : '' }
async function readJson(res) { const text = await res.text(); try { return text ? JSON.parse(text) : null } catch { return { error: text.slice(0, 500) } } }
function cleanApiError(data, fallback = '请求失败') {
  const raw = data?.message || data?.msg || data?.error || data?.detail || fallback
  const text = String(raw || fallback)
  if (/<!doctype html|<html|error response|nothing matches the given uri/i.test(text)) return '接口暂未生效，请刷新后重试；若仍失败请联系管理员。'
  return text.length > 180 ? text.slice(0, 180) + '…' : text
}
const BACKEND_BASE_KEY = 'WEIREN_BACKEND_BASE'
const DEFAULT_BACKEND_BASE = 'https://s-63a86395-de5c-46f9-a54d-0f7d02aa0671-3000.cohub.run'
function normalizeBackendBase(value) {
  const raw = String(value || '').trim().replace(/\/$/, '')
  if (!raw || !/^https:\/\//i.test(raw)) return ''
  return raw
}
function initBackendBase() {
  try {
    const url = new URL(window.location.href)
    const fromQuery = normalizeBackendBase(url.searchParams.get('backend') || url.searchParams.get('api'))
    if (fromQuery) {
      localStorage.setItem(BACKEND_BASE_KEY, fromQuery)
      url.searchParams.delete('backend')
      url.searchParams.delete('api')
      window.history.replaceState({}, document.title, `${url.pathname}${url.search}${url.hash}`)
      return fromQuery
    }
  } catch {}
  return normalizeBackendBase(window.__BACKEND_BASE__) || normalizeBackendBase(localStorage.getItem(BACKEND_BASE_KEY)) || normalizeBackendBase(DEFAULT_BACKEND_BASE)
}
const BACKEND_BASE = initBackendBase()
function apiUrl(path) {
  const raw = String(path || '')
  if (/^https?:\/\//i.test(raw)) return raw
  if (raw.startsWith('/api/') && BACKEND_BASE) return `${BACKEND_BASE}${raw}`
  return raw
}
async function api(path, options = {}) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), options.timeout || 20000)
  try {
    const res = await fetch(apiUrl(path), { ...options, signal: controller.signal })
    const data = await readJson(res)
    if (!res.ok) throw new Error(cleanApiError(data, res.statusText))
    return data
  } catch (e) {
    if (e.name === 'AbortError') throw new Error('请求超时，请稍后重试')
    throw e
  } finally {
    clearTimeout(timeout)
  }
}
function fileExt(file) { return (file?.name?.split('.').pop() || 'png').toLowerCase().replace(/[^a-z0-9]/g, '') || 'png' }
function loadImageLibrary() {
  try { return JSON.parse(localStorage.getItem(IMAGE_LIBRARY_KEY) || '[]').filter(x => x?.url).slice(0, 60) } catch { return [] }
}
function saveImageLibrary() { localStorage.setItem(IMAGE_LIBRARY_KEY, JSON.stringify(imageLibrary.value.slice(0, 60))) }
function addImageToLibrary(url, name = '') {
  if (!url) return
  imageLibrary.value = [{ url, name, time: Date.now() }, ...imageLibrary.value.filter(x => x.url !== url)].slice(0, 60)
  saveImageLibrary()
}
function useLibraryImage(target, url) {
  if (!target.value.includes(url)) target.value.push(url)
  showMsg('已从本地图片库添加', 'ok')
}
function fileToBase64(file, task) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => { if (task) task.progress = Math.max(task.progress, 35); resolve(String(reader.result || '').split(',', 2)[1] || '') }
    reader.onerror = () => reject(new Error('图片读取失败'))
    reader.onprogress = e => { if (task && e.lengthComputable) task.progress = Math.min(30, Math.round((e.loaded / e.total) * 30)) }
    reader.readAsDataURL(file)
  })
}
async function uploadImageToGallery(file, task) {
  if (!session.token) throw new Error('请先登录')
  if (file.size > 5 * 1024 * 1024) throw new Error('图片不能超过 5MB')
  const data = await fileToBase64(file, task)
  if (task) task.progress = Math.max(task.progress, 42)
  const progressTimer = setInterval(() => { if (task && task.status === 'uploading') task.progress = Math.min(88, task.progress + 3) }, 700)
  try {
    const res = await api('/api/proxy/upload-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-token': session.token },
      body: JSON.stringify({ suffix: fileExt(file), data }),
      timeout: 90000
    })
    if (task) task.progress = 100
    return res?.url
  } finally {
    clearInterval(progressTimer)
  }
}
async function handleImageFiles(files, target) {
  const list = Array.from(files || []).filter(f => f.type.startsWith('image/'))
  if (!list.length) return
  showMsg(`开始上传 ${list.length} 张图片...`, 'muted')
  for (const file of list) {
    const task = reactive({ id: `${Date.now()}-${Math.random()}`, name: file.name || '图片', progress: 0, status: 'uploading', error: '' })
    uploadTasks.value.unshift(task)
    try {
      const url = await uploadImageToGallery(file, task)
      if (url) {
        target.value.push(url)
        addImageToLibrary(url, file.name || '图片')
        task.status = 'done'; task.progress = 100
      } else {
        throw new Error('未返回图片链接')
      }
    } catch (e) {
      task.status = 'error'; task.error = e.message || '上传失败'; task.progress = Math.max(task.progress, 6)
      showMsg(`图片上传失败：${task.error}`)
    }
  }
  if (!uploadTasks.value.some(t => t.status === 'uploading')) showMsg('图片上传完成，可在页面预览或从本地图片库复用', 'ok')
}
function onForumImages(e) { handleImageFiles(e.target.files, uploadedForumImages); e.target.value = '' }
function onWikiImages(e) { handleImageFiles(e.target.files, uploadedWikiImages); e.target.value = '' }
function removeUploadedImage(target, url) { target.value = target.value.filter(x => x !== url) }
async function loadForumPosts(force = false) {
  const channel = selectedForum.value
  if (!force && forumFresh(channel) && forumPosts.value.length) return
  const seq = ++forumSeq.value
  forumLoading.value = true
  try {
    const rows = await api(`/api/forum/posts?channel=${encodeURIComponent(channel)}`)
    if (seq === forumSeq.value) {
      forumPosts.value = Array.isArray(rows) ? rows.reverse() : []
      markForum(channel)
    }
  } catch (e) {
    if (seq === forumSeq.value) forumPosts.value = []
  } finally {
    if (seq === forumSeq.value) forumLoading.value = false
  }
}
async function postForumMessage() {
  if (!session.token) { showMsg('请先登录后再发言'); return }
  if (['活动颁布', '成员'].includes(selectedForum.value)) { showMsg('当前栏目不是论坛发言区', 'muted'); return }
  if (forumPosting.value || (!forumText.value && !uploadedForumImages.value.length)) return
  forumPosting.value = true
  try {
    await api('/api/forum/posts', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ channel: selectedForum.value, content: forumText.value, images: uploadedForumImages.value }) })
    forumText.value = ''; uploadedForumImages.value = []
    await loadForumPosts(true)
    showMsg('已发送', 'ok')
  } catch (e) { showMsg(`发送失败：${e.message}`) } finally { forumPosting.value = false }
}

function initCaptcha() {
  return new Promise((resolve, reject) => {
    if (!window.initGeetest4) { reject(new Error('验证码组件加载失败，请刷新页面')); return }
    let done = false
    const timeout = setTimeout(() => { if (!done) { done = true; reject(new Error('验证码加载超时（网络问题），请稍后重试')) } }, 10000)
    window.initGeetest4({ captchaId: 'e000881b946cad6dcc39aa1eb40c80b0', product: 'popup', protocol: 'https://', hideSuccess: true, mask: { outside: false } }, (obj) => {
      clearTimeout(timeout)
      if (done) return
      obj.onSuccess(() => { const v = obj.getValidate(); obj.destroy(); resolve(v) })
      obj.onError(() => { obj.destroy(); reject(new Error('安全验证出错，请重试')) })
      obj.onClose(() => { obj.destroy(); reject(new Error('验证已取消')) })
      obj.onReady(() => obj.showCaptcha())
    })
  })
}
async function loadCaptchaScript() {
  if (window.initGeetest4) return
  await new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://oss.talesofai.cn/fe_assets/libs/gt4.js'
    s.async = true
    s.onload = resolve
    s.onerror = () => reject(new Error('验证码脚本加载失败'))
    document.head.appendChild(s)
  })
}
async function sendCode() {
  const p = phone.value
  if (!vp(p)) return showMsg('请输入正确的手机号')
  sending.value = true
  try {
    showMsg('加载验证码...', 'muted')
    await loadCaptchaScript()
    const captcha_validate = await initCaptcha()
    showMsg('发送中...', 'muted')
    const data = await api('/api/proxy/request-code', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone_num: p, captcha_validate }) })
    showMsg(data?.duration ? `验证码已发送，${data.duration}s 内有效` : '验证码已发送', 'ok')
    timer.value = 60
    const id = setInterval(() => { timer.value -= 1; if (timer.value <= 0) clearInterval(id) }, 1000)
  } catch (e) { showMsg(`发送失败：${e.message}`) } finally { sending.value = false }
}
async function login() {
  const p = phone.value, c = code.value
  if (!vp(p)) return showMsg('请输入正确的手机号')
  if (!/^\d{4}$/.test(c)) return showMsg('请输入4位验证码')
  if (!agree.value) return showMsg('请先阅读并同意协议')
  logging.value = true
  try {
    const data = await api('/api/proxy/verify-code', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone_num: p, code: c }) })
    if (!data?.token) throw new Error('未获取到令牌')
    await useToken(data.token)
  } catch (e) { showMsg(`登录失败：${e.message}`) } finally { logging.value = false }
}
async function useToken(token) {
  const me = await api(`${API}/v1/user/`, { headers: { 'x-token': token } })
  if (!me?.uuid) throw new Error('令牌无效')
  // Token 本地保存：仅写入用户浏览器 localStorage，不上传后端持久化。
  session.me = me; session.token = token; localStorage.setItem(TOKEN_KEY, token)
  const verified = await api('/api/verify', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': token }, body: JSON.stringify(me) }).catch(() => null)
  const role = await api(`/api/members/role?uuid=${encodeURIComponent(me.uuid)}`)
  session.role = role?.role || verified?.role || 'member'
  avatarFrame.value = ['none', 'roach', 'moonrise'].includes(role?.avatar_frame) ? role.avatar_frame : (['none', 'roach', 'moonrise'].includes(verified?.avatar_frame) ? verified.avatar_frame : 'none')
  signatureText.value = role?.signature ?? verified?.signature ?? ''
  localStorage.setItem('NIETA_AVATAR_FRAME', avatarFrame.value)
  await loadMembers(true)
  await loadWikiArchive(true)
  await loadForumMeta(true)
  await loadForumPosts(true)
  await loadIdentityCards(true)
}
async function loadMembers(force = false) {
  if (!force && cacheFresh('members') && members.value.length) return
  members.value = await api('/api/members').catch(() => [])
  const mine = members.value.find(m => m.uuid === session.me?.uuid)
  if (mine) signatureText.value = mine.signature || ''
  markCache('members')
}
async function searchEntries() {
  const q = globalQuery.value.trim()
  const seq = ++searchSeq.value
  serverResults.value = []
  if (!q) return
  searchLoading.value = true
  try {
    const rows = await api(`/api/search?q=${encodeURIComponent(q)}`)
    if (seq === searchSeq.value) serverResults.value = Array.isArray(rows) ? rows : []
  } catch {
    if (seq === searchSeq.value) serverResults.value = []
  } finally {
    if (seq === searchSeq.value) searchLoading.value = false
  }
}
function confirmPendingUpload() {
  if (!uploadInProgress.value) return true
  return window.confirm('还有图片上传任务未完成，切换页面可能导致上传结果没有加入当前编辑内容。确定要离开吗？')
}
function navigate(nextView) { if (!confirmPendingUpload()) return; view.value = nextView; currentEntry.value = null; window.scrollTo({ top: 0, behavior: 'instant' }) }
function openForum() { navigate('forum'); globalQuery.value = ''; serverResults.value = []; loadMembers(); loadForumMeta(); loadForumPosts() }
function openArchive() { navigate('archive'); currentCat.value = ''; catQuery.value = ''; selectedWikiGroup.value = ''; selectedWikiSubsection.value = ''; selectedWikiCategory.value = ''; selectedArtifactCategory.value = ''; wikiSubmitOpen.value = false; loadMembers(); loadWikiArchive(); loadForumMeta() }
function enterWikiGroup(group) { selectedWikiGroup.value = group; selectedWikiSubsection.value = ''; selectedWikiCategory.value = ''; selectedArtifactCategory.value = ''; wikiSubmitOpen.value = false; window.scrollTo(0, 0) }
function leaveWikiLevel() { if (selectedWikiGroup.value === '世界信息') { if (selectedWikiCategory.value) { selectedWikiCategory.value = ''; wikiSubmitOpen.value = false; return } if (selectedWikiSubsection.value) { selectedWikiSubsection.value = ''; return } selectedWikiGroup.value = ''; return } if (selectedWikiGroup.value === '伪物档案') { if (selectedArtifactCategory.value) { selectedArtifactCategory.value = ''; wikiSubmitOpen.value = false; return } selectedWikiGroup.value = '' } }
function openExplore() { navigate('explore') }
function openCategory(cat) { currentCat.value = cat; catQuery.value = ''; navigate('category') }
async function openEntry(uuid, fromGlobal = false) { if (!confirmPendingUpload()) return; const entry = allEntries.value.find(e => e.uuid === uuid); if (!entry) return; currentEntry.value = entry; currentCat.value = entry.category; view.value = 'entry'; if (fromGlobal) globalQuery.value = ''; window.scrollTo({ top: 0, behavior: 'instant' }); await loadComments(uuid) }
async function loadComments(uuid) { comments.value = await api(`/api/comments?entry_uuid=${encodeURIComponent(uuid)}`).catch(() => []); commentCounts.value = { ...commentCounts.value, [uuid]: comments.value.length } }
async function postComment() { if (!currentEntry.value || !commentText.value) return; posting.value = true; try { await api('/api/comments', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ entry_uuid: currentEntry.value.uuid, content: commentText.value }) }); commentText.value = ''; await loadComments(currentEntry.value.uuid) } finally { posting.value = false } }
function logout() { localStorage.removeItem(TOKEN_KEY); session.me = null; session.token = ''; session.role = 'member'; view.value = 'forum' }
function badgeMark(d = '') { return ['🟥', '🟧', '🟨', '🟩', '⬜'].find(x => d.includes(x)) || '' }
function badgeClass(d = '') { const m = badgeMark(d); return { '🟥': 'b-red', '🟧': 'b-orange', '🟨': 'b-yellow', '🟩': 'b-green', '⬜': 'b-gray' }[m] || 'b-gray' }
function timeAgo(ts) { if (!ts) return ''; const d = Date.now() / 1000 - Number(ts); if (d < 0) return '在线'; if (d < 60) return '刚刚在线'; if (d < 3600) return `${Math.floor(d / 60)}分钟前`; if (d < 86400) return `${Math.floor(d / 3600)}小时前`; return `${Math.floor(d / 86400)}天前` }

function tickLiveUsers() {
  const base = 37
  const wave = Math.round(Math.sin(Date.now() / 18000) * 6)
  const jitter = Math.floor(Math.random() * 5) - 2
  liveUserCount.value = Math.max(24, Math.min(52, base + wave + jitter))
}

function beforeUnloadUploadGuard(e) {
  if (!uploadInProgress.value) return
  e.preventDefault()
  e.returnValue = '还有图片上传任务未完成，确定要离开吗？'
}
onBeforeUnmount(() => { clearInterval(identityCardProgressTimer); clearInterval(liveUserTimer); window.removeEventListener('beforeunload', beforeUnloadUploadGuard) })

onMounted(async () => {
  window.addEventListener('beforeunload', beforeUnloadUploadGuard)
  tickLiveUsers()
  liveUserTimer = setInterval(tickLiveUsers, 4500)
  await loadWikiArchive()
  const saved = localStorage.getItem(TOKEN_KEY)
  if (saved) { logging.value = true; showMsg('检测到已保存的登录状态', 'muted'); try { await useToken(saved) } catch { localStorage.removeItem(TOKEN_KEY); showMsg('登录状态已过期，请重新登录') } finally { logging.value = false } }
})
</script>
