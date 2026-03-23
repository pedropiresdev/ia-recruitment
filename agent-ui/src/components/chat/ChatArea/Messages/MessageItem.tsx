import Icon from '@/components/ui/icon'
import MarkdownRenderer from '@/components/ui/typography/MarkdownRenderer'
import { useStore } from '@/store'
import type { ChatMessage } from '@/types/os'
import Videos from './Multimedia/Videos'
import Images from './Multimedia/Images'
import Audios from './Multimedia/Audios'
import { memo, useMemo } from 'react'
import AgentThinkingLoader from './AgentThinkingLoader'
import { ProcessDashboardWidget } from '@/components/recruitment/ProcessDashboardWidget'
import { ProcessDetailWidget } from '@/components/recruitment/ProcessDetailWidget'
import { CandidateBoardWidget } from '@/components/recruitment/CandidateBoardWidget'
import { CandidateProfileWidget } from '@/components/recruitment/CandidateProfileWidget'
import { InterviewWidget } from '@/components/recruitment/InterviewWidget'
import { SchedulingOptionsWidget } from '@/components/recruitment/SchedulingOptionsWidget'
import type { RecruitmentProcess } from '@/types/recruitment'
import type { ProcessDetailWidgetData } from '@/components/recruitment/ProcessDetailWidget'
import type { CandidateBoardWidgetData } from '@/components/recruitment/CandidateBoardWidget'
import type { CandidateProfileWidgetData } from '@/components/recruitment/CandidateProfileWidget'
import type { InterviewWidgetData } from '@/components/recruitment/InterviewWidget'
import type { SchedulingOptionsWidgetData } from '@/components/recruitment/SchedulingOptionsWidget'

interface MessageProps {
  message: ChatMessage
}

type Widget =
  | { __widget: 'process_dashboard'; summary?: string; kpis: { total: number; em_atraso: number; em_risco: number; no_prazo: number }; items: RecruitmentProcess[] }
  | { __widget: 'process_list'; items: RecruitmentProcess[] }
  | ({ __widget: 'process_detail' } & ProcessDetailWidgetData)
  | ({ __widget: 'candidate_board' } & CandidateBoardWidgetData)
  | ({ __widget: 'candidate_profile' } & CandidateProfileWidgetData)
  | InterviewWidgetData
  | SchedulingOptionsWidgetData

/** Extracts the last ```json block containing a __widget field. */
function extractWidget(content: string): { clean: string; widget: Widget | null } {
  const fenceRe = /```json\s*\n(\{[\s\S]*?"__widget"[\s\S]*?\})\s*\n```/g
  let last: RegExpExecArray | null = null
  let match: RegExpExecArray | null
  while ((match = fenceRe.exec(content)) !== null) last = match
  if (!last) return { clean: content, widget: null }

  try {
    const parsed = JSON.parse(last[1])
    if (typeof parsed.__widget === 'string') {
      const clean = content.replace(last[0], '').trim()
      return { clean, widget: parsed as Widget }
    }
  } catch {
    // invalid JSON — ignore
  }
  return { clean: content, widget: null }
}

const AgentMessage = ({ message }: MessageProps) => {
  const { streamingErrorMessage } = useStore()

  const { clean, widget } = useMemo(
    () => (message.content ? extractWidget(message.content) : { clean: '', widget: null }),
    [message.content]
  )

  let messageContent
  if (message.streamingError) {
    messageContent = (
      <p className="text-destructive">
        Oops! Something went wrong while streaming.{' '}
        {streamingErrorMessage ? (
          <>{streamingErrorMessage}</>
        ) : (
          'Please try refreshing the page or try again later.'
        )}
      </p>
    )
  } else if (message.content) {
    messageContent = (
      <div className="flex w-full flex-col gap-2">
        {clean && <MarkdownRenderer>{clean}</MarkdownRenderer>}

        {widget?.__widget === 'process_dashboard' && (
          <ProcessDashboardWidget
            summary={widget.summary}
            kpis={widget.kpis}
            items={widget.items}
          />
        )}

        {widget?.__widget === 'process_list' && (
          <ProcessDashboardWidget
            kpis={{
              total: widget.items.length,
              em_atraso: widget.items.filter((p) => p.sla_status === 'em_atraso').length,
              em_risco: widget.items.filter((p) => p.sla_status === 'em_risco').length,
              no_prazo: widget.items.filter((p) => p.sla_status === 'no_prazo').length,
            }}
            items={widget.items}
          />
        )}

        {widget?.__widget === 'process_detail' && (
          <ProcessDetailWidget {...widget} />
        )}

        {widget?.__widget === 'candidate_board' && (
          <CandidateBoardWidget {...widget} />
        )}

        {widget?.__widget === 'candidate_profile' && (
          <CandidateProfileWidget {...widget} />
        )}

        {(widget?.__widget === 'interview_list' || widget?.__widget === 'interview_card') && (
          <InterviewWidget {...(widget as InterviewWidgetData)} />
        )}

        {widget?.__widget === 'scheduling_options' && (
          <SchedulingOptionsWidget {...(widget as SchedulingOptionsWidgetData)} />
        )}

        {message.videos && message.videos.length > 0 && (
          <Videos videos={message.videos} />
        )}
        {message.images && message.images.length > 0 && (
          <Images images={message.images} />
        )}
        {message.audio && message.audio.length > 0 && (
          <Audios audio={message.audio} />
        )}
      </div>
    )
  } else if (message.response_audio) {
    if (!message.response_audio.transcript) {
      messageContent = (
        <div className="mt-2 flex items-start">
          <AgentThinkingLoader />
        </div>
      )
    } else {
      messageContent = (
        <div className="flex w-full flex-col gap-4">
          <MarkdownRenderer>{message.response_audio.transcript}</MarkdownRenderer>
          {message.response_audio.content && (
            <Audios audio={[message.response_audio]} />
          )}
        </div>
      )
    }
  } else {
    messageContent = (
      <div className="mt-2">
        <AgentThinkingLoader />
      </div>
    )
  }

  return (
    <div className="flex flex-row items-start gap-4 font-geist">
      <div className="flex-shrink-0">
        <Icon type="agent" size="sm" />
      </div>
      {messageContent}
    </div>
  )
}

const UserMessage = memo(({ message }: MessageProps) => {
  return (
    <div className="flex items-start gap-4 pt-4 text-start max-md:break-words">
      <div className="flex-shrink-0">
        <Icon type="user" size="sm" />
      </div>
      <div className="text-md rounded-lg font-geist text-secondary">
        {message.content}
      </div>
    </div>
  )
})

AgentMessage.displayName = 'AgentMessage'
UserMessage.displayName = 'UserMessage'
export { AgentMessage, UserMessage }
