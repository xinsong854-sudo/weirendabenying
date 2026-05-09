<template>
  <section v-if="!session.me" class="login-scene">
    <div class="login-card labyrinth-window">
      <div class="window-title">IDENTITY RITUAL</div>
      <div class="emblem">✦</div>
      <h1>伪人大本营</h1>
      <p class="tagline">机密档案库 · 身份核验</p>
      <div class="field"><span class="prefix">+86</span><input v-model.trim="phone" type="tel" inputmode="numeric" maxlength="11" placeholder="请输入手机号" autocomplete="tel"></div>
      <div class="field"><input v-model.trim="code" type="text" inputmode="numeric" maxlength="4" placeholder="验证码" autocomplete="one-time-code"><button class="code-btn" :disabled="sending || timer > 0" @click="sendCode">{{ timer > 0 ? `${timer}s` : '获取验证码' }}</button></div>
      <label class="agree"><input v-model="agree" type="checkbox"><span>我已阅读并同意 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/user-agreement.html" target="_blank" rel="noopener noreferrer">用户协议</a> 和 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/privacy-policy.html" target="_blank" rel="noopener noreferrer">隐私政策</a></span></label>
      <button class="submit" :disabled="logging" @click="login">{{ logging ? '登录中...' : '登 录' }}</button>
      <div class="msg" :class="messageType">{{ message }}</div>
      <div class="foot">未注册手机号验证后将自动登录 · t.nieta.art/UTLCFvWs</div>
    </div>
  </section>

  <section v-else class="labyrinth-app">
    <div v-if="message" class="global-toast" :class="messageType">{{ message }}</div>
    <main class="stage-main">
      <Transition name="page-shift" mode="out-in">
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
                  <header class="friend-detail-head"><button class="detail-avatar" @click.stop.prevent="openMemberModal(selectedMember)"><span class="framed-avatar" :class="avatarFrameClassFor(selectedMember)"><img class="avatar-base" v-if="safeUrl(selectedMember.avatar)" :src="safeUrl(selectedMember.avatar)" alt="" referrerpolicy="no-referrer"><b v-else>{{ initials(selectedMember.name) }}</b><img v-if="avatarFrameFor(selectedMember)?.type === 'frame'" class="avatar-frame" :src="avatarFrameFor(selectedMember).url" alt=""><span v-if="avatarFrameFor(selectedMember)?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="avatarFrameFor(selectedMember).url" alt=""></span></span></button><div><h2>{{ selectedMember.name }} <span v-if="['chief','deputy','admin'].includes(selectedMember.role)" class="verify-v">V</span></h2><p v-if="memberTitle(selectedMember)">{{ memberTitle(selectedMember) }}</p><small>{{ selectedMember.online ? '在线' : timeAgo(selectedMember.last_seen) }}</small></div><div class="detail-actions"><button class="title-auth-btn" @click="openPrivatePane(selectedMember)">私聊</button><button v-if="isAdmin" class="title-auth-btn" @click="authorizeTitle(selectedMember)">授权称号</button></div></header>
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
              <header><div><span>栏目 / {{ selectedWikiCategory }}</span><h3>{{ selectedWikiCategory }}</h3></div><div class="wiki-actions inline"><input ref="wikiUploadInput" class="hidden-file" type="file" accept="image/*" multiple @change="onWikiImages"><button class="back-note" @click="openCategory(selectedWikiCategory)">查看全部词条</button><button class="back-note" @click="wikiUploadInput?.click()">上传图片</button><button class="back-note" @click="wikiSubmitType = '修订词条'; wikiSubmitOpen = !wikiSubmitOpen">提交编辑</button><button class="back-note" @click="wikiSubmitType = '开新栏目'; wikiSubmitOpen = !wikiSubmitOpen">开新栏目</button></div></header>
              <div v-if="uploadedWikiImages.length" class="upload-preview wiki-preview"><span v-for="img in uploadedWikiImages" :key="img"><img :src="img" alt=""><button @click="removeUploadedImage(uploadedWikiImages, img)">×</button></span></div>
              <div v-if="wikiSubmitOpen" class="wiki-submit-panel"><div><b>{{ wikiSubmitType }}</b><p>提交目标：<strong>{{ selectedWikiCategory }}</strong></p></div><label>选择已有栏目作为归属<select v-model="selectedWikiCategory"><option v-for="name in wikiSubmissionTargets" :key="name" :value="name">{{ name }}</option></select></label><textarea v-model.trim="wikiSubmitContent" rows="4" :placeholder="wikiSubmitType === '开新栏目' ? '写明想开的栏目名称、归属栏目和用途...' : '写明要新增/修订的词条内容、图片链接或理由...'"></textarea><button class="back-note primary" :disabled="!wikiSubmitContent" @click="submitWikiChange">提交到待审核</button></div>
              <div class="wiki-entry-preview"><button v-for="entry in currentWikiCategoryPreview.slice(0, 12)" :key="entry.uuid" @click="openEntry(entry.uuid)">{{ entry.name }}</button></div>
            </div>
          </section>

          <section v-else-if="selectedWikiGroup === '伪物档案'" class="wiki-drill-panel artifact-drill">
            <header class="drill-head artifact"><div><span class="ritual-label">PSEUDO-ARTIFACTS ARCHIVE</span><h2>伪物档案</h2><p v-if="!selectedArtifactCategory">选择伪物档案下的子栏目。</p><p v-else>当前子栏目：{{ selectedArtifactCategory }}</p></div><button class="back-note" @click="leaveWikiLevel">返回上一级</button></header>
            <div v-if="!selectedArtifactCategory" class="drill-grid level-one">
              <button v-for="cat in artifactCategories" :key="cat.name" @click="selectedArtifactCategory = cat.name"><b>{{ cat.name }}</b><small>{{ cat.count }} 件记录</small><i>进入子栏目</i></button>
              <button class="artifact-add" @click="selectedArtifactCategory = artifactCategories[0]?.name || ''; wikiSubmitType = '开新栏目'; wikiSubmitOpen = !wikiSubmitOpen"><b>申请新图鉴栏目</b><small>向管理员提交新的伪物分类。</small><i>NEW</i></button>
            </div>
            <main v-else class="artifact-files standalone">
              <div class="artifact-warning"><b>内部图鉴 / {{ selectedArtifactCategory }}</b><span>伪物资料需管理员审核后公开</span></div>
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
            <div>
              <b>{{ session.me.nick_name || session.me.name }}</b>
              <small>{{ session.me.uuid }}</small>
            </div>
            <button class="logout-danger" @click="logout">退出登录</button>
          </div>
          <div class="profile-tabs">
            <button :class="{ active: activeProfilePanel === 'overview' }" @click="activeProfilePanel = 'overview'">概览</button>
            <button :class="{ active: activeProfilePanel === 'frames' }" @click="activeProfilePanel = 'frames'">头像框</button>
            <button :class="{ active: activeProfilePanel === 'card' }" @click="activeProfilePanel = 'card'">身份卡</button>
            <button v-if="isAdmin" :class="{ active: activeProfilePanel === 'review' }" @click="activeProfilePanel = 'review'">待审核</button>
          </div>
          <div v-if="activeProfilePanel === 'overview'" class="setting-block">
            <h3>个人概览</h3>
            <p>这里是你的营地身份页。点击上方栏目查看头像框、身份卡或管理员审核内容。</p>
          </div>
          <div v-else-if="activeProfilePanel === 'frames'" class="setting-block">
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
          <div v-else-if="activeProfilePanel === 'card'" class="setting-block identity-card-block">
            <h3>身份卡</h3>
            <p>身份卡功能等会开放。未来可展示阵营、称号、通行许可与个人签名。</p>
            <button class="back-note" disabled>即将开放</button>
          </div>
          <div v-else-if="isAdmin && activeProfilePanel === 'review'" class="setting-block review-block">
            <h3>待审核 Wiki 内容</h3>
            <p>成员提交的新增词条与修订会出现在这里，管理员审核通过后进入 Wiki。</p>
            <div v-for="item in pendingWiki" :key="item.id" class="review-item">
              <b>{{ item.target }}</b><span>{{ item.type }}</span><small>{{ item.author }} · {{ timeAgo(item.time) }}</small><p>{{ item.content }}</p>
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
        <h2>{{ selectedMemberModal.name }} <span v-if="['chief','deputy','admin'].includes(selectedMemberModal.role)" class="verify-v">V</span></h2>
        <p v-if="memberTitle(selectedMemberModal)">{{ memberTitle(selectedMemberModal) }}</p>
        <small>{{ selectedMemberModal.online ? '在线' : timeAgo(selectedMemberModal.last_seen) }}</small>
        <button v-if="isAdmin" class="title-auth-btn" @click="authorizeTitle(selectedMemberModal)">授权称号</button>
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
import { computed, onMounted, reactive, ref } from 'vue'
import archive from './pseudo-human-data.json'

const API = 'https://api.talesofai.cn'
const TOKEN_KEY = 'NIETA_ACCESS_TOKEN'
// Forum channels and activities are persisted by backend APIs, not localStorage.
const phone = ref('')
const code = ref('')
const agree = ref(false)
const message = ref('')
const messageType = ref('')
const sending = ref(false)
const logging = ref(false)
const timer = ref(0)
const view = ref('forum')
const currentCat = ref('')
const currentEntry = ref(null)
const globalQuery = ref('')
const serverResults = ref([])
const searchLoading = ref(false)
const searchSeq = ref(0)
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
const privateText = ref('')
const selectedWikiGroup = ref('')
const selectedWikiCategory = ref('')
const selectedWikiSubsection = ref('')
const selectedArtifactCategory = ref('')
const wikiSubmitOpen = ref(false)
const wikiSubmitType = ref('修订词条')
const wikiSubmitContent = ref('')
const activeProfilePanel = ref('overview')
const forumUploadInput = ref(null)
const wikiUploadInput = ref(null)
const uploadedForumImages = ref([])
const uploadedWikiImages = ref([])
const savedFrame = localStorage.getItem('NIETA_AVATAR_FRAME')
const avatarFrame = ref(['none', 'roach', 'moonrise'].includes(savedFrame) ? savedFrame : 'roach')
const session = reactive({ me: null, role: 'member', token: '' })
const avatarFrames = [
  { id: 'none', name: '无头像框', url: '', type: 'none' },
  { id: 'roach', name: '乱爬蟑螂', url: 'https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/53710f82-1ad8-4863-98ee-4d7bed45f215.png', type: 'roach' },
  { id: 'moonrise', name: '月升', url: 'https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/5e22d7db-3abd-4861-864e-725538d3794b.png', type: 'frame' }
]

const allEntries = Object.entries(archive.lore).flatMap(([category, entries]) => entries.map(e => ({ ...e, category })))
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
const artifactEntries = computed(() => archive.lore[selectedArtifactCategory.value] || [])
const isAdmin = computed(() => ['chief', 'deputy', 'admin'].includes(session.role))
const forumBranches = [
  { code: 'MAIN', name: '主论坛', desc: '公告、规则、日常讨论与营地事务。' },
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
const selectedForumDescription = computed(() => {
  const branch = [...forumBranches, ...customForumBranches.value].find(x => x.name === selectedForum.value)
  const col = forumColumns.find(x => x.name === selectedForum.value)
  return branch?.desc || col?.desc || '论坛频道'
})
const visibleThreads = computed(() => forumPosts.value.filter(t => !t.revoked))
const globalResults = computed(() => {
  const q = globalQuery.value.trim()
  if (!q) return []
  return serverResults.value.length ? serverResults.value : filterEntries(allEntries, q).slice(0, 20)
})
const categoryEntries = computed(() => filterEntries(archive.lore[currentCat.value] || [], catQuery.value))
const sortedMembers = computed(() => [...members.value].sort((a, b) => Number(b.online) - Number(a.online) || (Number(b.last_seen || 0) - Number(a.last_seen || 0))))
const filteredMembers = computed(() => {
  const q = memberQuery.value.toLowerCase()
  return sortedMembers.value.filter(m => !q || `${m.name} ${memberTitle(m)}`.toLowerCase().includes(q))
})
const currentAvatarFrame = computed(() => avatarFrames.find(f => f.id === avatarFrame.value && f.url) || null)
const avatarFrameClass = computed(() => currentAvatarFrame.value ? (currentAvatarFrame.value.type === 'roach' ? 'has-roach-frame avatar-frame-roach' : `avatar-frame-${currentAvatarFrame.value.id}`) : '')
function avatarFrameFor(member) {
  const uid = member?.uuid || member?.user_uuid
  const frameId = uid && uid === session.me?.uuid ? avatarFrame.value : (member?.avatar_frame || 'none')
  return avatarFrames.find(f => f.id === frameId && f.url) || null
}
function avatarFrameClassFor(member) { const f = avatarFrameFor(member); return f ? (f.type === 'roach' ? 'has-roach-frame avatar-frame-roach' : `avatar-frame-${f.id}`) : '' }

function makeBranchCode(name) { return String(name || 'NEW').trim().replace(/\s+/g, '').slice(0, 4).toUpperCase() || 'NEW' }
async function loadForumMeta() {
  const [channels, acts, wikiRows] = await Promise.all([
    api('/api/forum/channels').catch(() => []),
    api('/api/activities').catch(() => []),
    api('/api/wiki/submissions').catch(() => [])
  ])
  customForumBranches.value = Array.isArray(channels) ? channels : []
  customActivities.value = Array.isArray(acts) ? acts : []
  pendingWiki.value = Array.isArray(wikiRows) ? wikiRows : []
}
async function createForumBranch() {
  const name = window.prompt('新分支名称：')?.trim()
  if (!name) return
  const exists = [...forumBranches, ...forumColumns, ...customForumBranches.value].some(x => x.name === name)
  if (exists) { showMsg('这个分支/频道已经存在'); return }
  const desc = window.prompt('分支说明（可留空）：', `${name}地区分支讨论区。`)?.trim() || `${name}地区分支讨论区。`
  try {
    await api('/api/forum/channels', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ code: makeBranchCode(name), name, desc }) })
    await loadForumMeta()
    selectedForumGroup.value = '地区分支'; selectedForum.value = name.slice(0, 30); await loadForumPosts(); showMsg('新分支已创建', 'ok')
  } catch (e) { showMsg(`创建失败：${e.message}`) }
}
async function deleteForumBranch(item) {
  if (!item?.custom) return
  if (!window.confirm(`删除分支「${item.name}」？\n只会删除分支入口，不会删除该频道历史发言。`)) return
  try {
    await api('/api/forum/channels/delete', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ name: item.name }) })
    await loadForumMeta()
    if (selectedForum.value === item.name) selectedForum.value = forumBranches[1]?.name || '渊'
    await loadForumPosts(); showMsg('分支入口已删除', 'muted')
  } catch (e) { showMsg(`删除失败：${e.message}`) }
}
async function createActivity() {
  const title = window.prompt('活动标题：')?.trim()
  if (!title) return
  if (currentActivities.value.some(x => x.title === title)) { showMsg('这个活动已经存在'); return }
  const desc = window.prompt('活动说明：', '写下活动规则、时间、奖励或投稿方式。')?.trim() || '暂无说明。'
  const status = window.prompt('活动状态：', '进行中')?.trim() || '进行中'
  try {
    await api('/api/activities', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ title, status, desc }) })
    await loadForumMeta(); showMsg('活动已新增', 'ok')
  } catch (e) { showMsg(`新增活动失败：${e.message}`) }
}
async function deleteActivity(event) {
  if (!event?.custom) return
  if (!window.confirm(`删除活动「${event.title}」？`)) return
  try {
    await api('/api/activities/delete', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ id: event.id }) })
    await loadForumMeta(); showMsg('活动已删除', 'muted')
  } catch (e) { showMsg(`删除活动失败：${e.message}`) }
}
async function submitWikiChange() {
  if (!selectedWikiCategory.value || !wikiSubmitContent.value) return
  try {
    await api('/api/wiki/submissions', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ target: selectedWikiCategory.value, type: wikiSubmitType.value, content: wikiSubmitContent.value, images: uploadedWikiImages.value }) })
    wikiSubmitContent.value = ''; uploadedWikiImages.value = []; wikiSubmitOpen.value = false
    await loadForumMeta(); showMsg('已提交到后端待审核', 'ok')
  } catch (e) { showMsg(`提交失败：${e.message}`) }
}
function filterEntries(list, q) {
  const needle = String(q || '').toLowerCase()
  if (!needle) return list
  return list.filter(e => `${e.name}\n${e.description}`.toLowerCase().includes(needle))
}
function vp(p) { return /^1[3456789]\d{9}$/.test(p) }
function memberTitle(m) { return (m?.title || '').trim() }
function initials(name = '') { return String(name || '?').trim().slice(0, 1).toUpperCase() || '?' }
function showMsg(text, type = 'error') { message.value = text; messageType.value = type; clearTimeout(showMsg._t); showMsg._t = setTimeout(() => { if (message.value === text) message.value = '' }, type === 'error' ? 3200 : 1500) }
async function authorizeTitle(member) {
  const title = window.prompt(`给 ${member.name} 授权称号：`, member.title || '')
  if (title === null) return
  try {
    await api('/api/members/title', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ uuid: member.uuid, title }) })
    await loadMembers()
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
function openMemberModal(member) { selectedMember.value = member; selectedMemberTool.value = '资料'; selectedMemberModal.value = { ...member } }
function closeMemberModal() { selectedMemberModal.value = null }
function openProfile() { view.value = 'profile'; currentEntry.value = null; window.scrollTo(0, 0) }
function selectForumGroup(group) { selectedForumGroup.value = group.name; selectedForum.value = group.items?.[0]?.name || selectedForum.value; loadForumPosts() }
async function revokeThread(id) { try { await api('/api/forum/revoke', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ id }) }); await loadForumPosts(); showMsg('已撤销发言', 'muted') } catch (e) { showMsg(`撤销失败：${e.message}`) } }
function selectAvatarFrame(id) { avatarFrame.value = id; showMsg('已选择头像框，点击确定后保存', 'muted') }
async function saveAvatarFrame() { const id = avatarFrame.value; localStorage.setItem('NIETA_AVATAR_FRAME', id); try { await api('/api/members/avatar-frame', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ avatar_frame: id }) }); members.value = members.value.map(m => m.uuid === session.me?.uuid ? { ...m, avatar_frame: id } : m); if (selectedMember.value?.uuid === session.me?.uuid) selectedMember.value = { ...selectedMember.value, avatar_frame: id }; if (selectedMemberModal.value?.uuid === session.me?.uuid) selectedMemberModal.value = { ...selectedMemberModal.value, avatar_frame: id }; await loadMembers(); await loadForumPosts() } catch (e) { showMsg(`头像框保存失败：${e.message}`); return } showMsg(id === 'none' ? '已取消头像框' : '头像框已保存', 'ok') }
function openForumUser(thread) { const m = members.value.find(x => x.uuid === thread.user_uuid) || { uuid: thread.user_uuid, name: thread.user_name, avatar: thread.user_avatar, avatar_frame: thread.avatar_frame || 'none', online: false, last_seen: thread.created_at }; openMemberModal(m) }
function safeUrl(url) { const s = String(url || '').trim(); return /^(https?:)?\/\//i.test(s) ? s : '' }
async function readJson(res) { const text = await res.text(); try { return text ? JSON.parse(text) : null } catch { return { error: text.slice(0, 500) } } }
async function api(path, options) { const res = await fetch(path, options); const data = await readJson(res); if (!res.ok) throw new Error(data?.message || data?.msg || data?.error || data?.detail || res.statusText); return data }
function fileExt(file) { return (file?.name?.split('.').pop() || 'png').toLowerCase().replace(/[^a-z0-9]/g, '') || 'png' }
async function uploadImageToGallery(file) {
  if (!session.token) throw new Error('请先登录')
  const signed = await api(`${API}/v1/oss/upload-signed-url?suffix=${encodeURIComponent(fileExt(file))}`, { headers: { 'x-token': session.token } })
  const rawBlob = new Blob([file], { type: '' })
  const put = await fetch(signed.upload_url, { method: 'PUT', body: rawBlob })
  if (!put.ok) throw new Error(`OSS 上传失败：${put.status}`)
  const artifact = await api(`${API}/v1/artifact/picture`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ url: signed.view_url }) })
  return artifact?.url || artifact?.detail?.url || signed.view_url
}
async function handleImageFiles(files, target) {
  const list = Array.from(files || []).filter(f => f.type.startsWith('image/'))
  if (!list.length) return
  showMsg('图片上传到你的捏他图库中...', 'muted')
  try {
    for (const file of list) target.value.push(await uploadImageToGallery(file))
    showMsg('图片已上传到你的捏他图库，并使用图库链接显示', 'ok')
  } catch (e) { showMsg(`图片上传失败：${e.message}`) }
}
function onForumImages(e) { handleImageFiles(e.target.files, uploadedForumImages); e.target.value = '' }
function onWikiImages(e) { handleImageFiles(e.target.files, uploadedWikiImages); e.target.value = '' }
function removeUploadedImage(target, url) { target.value = target.value.filter(x => x !== url) }
async function loadForumPosts() {
  const seq = ++forumSeq.value
  forumLoading.value = true
  try {
    const rows = await api(`/api/forum/posts?channel=${encodeURIComponent(selectedForum.value)}`)
    if (seq === forumSeq.value) forumPosts.value = Array.isArray(rows) ? rows.reverse() : []
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
    await loadForumPosts()
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
  session.me = me; session.token = token; localStorage.setItem(TOKEN_KEY, token)
  await fetch('/api/verify', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': token }, body: JSON.stringify(me) }).catch(() => {})
  const role = await api(`/api/members/role?uuid=${encodeURIComponent(me.uuid)}`)
  session.role = role?.role || 'member'
  avatarFrame.value = ['none', 'roach', 'moonrise'].includes(role?.avatar_frame) ? role.avatar_frame : 'none'
  localStorage.setItem('NIETA_AVATAR_FRAME', avatarFrame.value)
  await loadMembers()
  await loadForumMeta()
  await loadForumPosts()
}
async function loadMembers() { members.value = await api('/api/members').catch(() => []) }
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
function openForum() { view.value = 'forum'; currentEntry.value = null; globalQuery.value = ''; serverResults.value = []; window.scrollTo(0, 0); loadMembers(); loadForumMeta(); loadForumPosts() }
function openArchive() { view.value = 'archive'; currentEntry.value = null; currentCat.value = ''; catQuery.value = ''; selectedWikiGroup.value = ''; selectedWikiSubsection.value = ''; selectedWikiCategory.value = ''; selectedArtifactCategory.value = ''; wikiSubmitOpen.value = false; window.scrollTo(0, 0); loadMembers(); loadForumMeta() }
function enterWikiGroup(group) { selectedWikiGroup.value = group; selectedWikiSubsection.value = ''; selectedWikiCategory.value = ''; selectedArtifactCategory.value = ''; wikiSubmitOpen.value = false; window.scrollTo(0, 0) }
function leaveWikiLevel() { if (selectedWikiGroup.value === '世界信息') { if (selectedWikiCategory.value) { selectedWikiCategory.value = ''; wikiSubmitOpen.value = false; return } if (selectedWikiSubsection.value) { selectedWikiSubsection.value = ''; return } selectedWikiGroup.value = ''; return } if (selectedWikiGroup.value === '伪物档案') { if (selectedArtifactCategory.value) { selectedArtifactCategory.value = ''; wikiSubmitOpen.value = false; return } selectedWikiGroup.value = '' } }
function openExplore() { view.value = 'explore'; currentEntry.value = null; window.scrollTo(0, 0) }
function openCategory(cat) { currentCat.value = cat; catQuery.value = ''; currentEntry.value = null; view.value = 'category'; window.scrollTo(0, 0) }
async function openEntry(uuid, fromGlobal = false) { const entry = allEntries.find(e => e.uuid === uuid); if (!entry) return; currentEntry.value = entry; currentCat.value = entry.category; view.value = 'entry'; if (fromGlobal) globalQuery.value = ''; window.scrollTo(0, 0); await loadComments(uuid) }
async function loadComments(uuid) { comments.value = await api(`/api/comments?entry_uuid=${encodeURIComponent(uuid)}`).catch(() => []); commentCounts.value = { ...commentCounts.value, [uuid]: comments.value.length } }
async function postComment() { if (!currentEntry.value || !commentText.value) return; posting.value = true; try { await api('/api/comments', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ entry_uuid: currentEntry.value.uuid, content: commentText.value }) }); commentText.value = ''; await loadComments(currentEntry.value.uuid) } finally { posting.value = false } }
function logout() { localStorage.removeItem(TOKEN_KEY); session.me = null; session.token = ''; session.role = 'member'; view.value = 'forum' }
function badgeMark(d = '') { return ['🟥', '🟧', '🟨', '🟩', '⬜'].find(x => d.includes(x)) || '' }
function badgeClass(d = '') { const m = badgeMark(d); return { '🟥': 'b-red', '🟧': 'b-orange', '🟨': 'b-yellow', '🟩': 'b-green', '⬜': 'b-gray' }[m] || 'b-gray' }
function timeAgo(ts) { if (!ts) return ''; const d = Date.now() / 1000 - Number(ts); if (d < 0) return '在线'; if (d < 60) return '刚刚在线'; if (d < 3600) return `${Math.floor(d / 60)}分钟前`; if (d < 86400) return `${Math.floor(d / 3600)}小时前`; return `${Math.floor(d / 86400)}天前` }

onMounted(async () => {
  const saved = localStorage.getItem(TOKEN_KEY)
  if (saved) { logging.value = true; showMsg('检测到已保存的登录状态', 'muted'); try { await useToken(saved) } catch { localStorage.removeItem(TOKEN_KEY); showMsg('登录状态已过期，请重新登录') } finally { logging.value = false } }
})
</script>
