import { CHATS } from "@/lib/content";

export function ChatMockups() {
  return (
    <section
      id="conversaciones"
      aria-labelledby="conversaciones-title"
      className="mx-auto max-w-5xl px-4 py-16"
    >
      <h2 id="conversaciones-title" className="text-center text-3xl font-bold">
        Una conversación, no un menú rígido
      </h2>
      <div className="mt-10 grid gap-8 md:grid-cols-2">
        {CHATS.map((chat) => (
          <figure key={chat.title} className="flex flex-col gap-3">
            <figcaption className="text-center font-semibold">{chat.title}</figcaption>
            <div className="flex flex-col gap-2 rounded-2xl bg-[#e7ded3] p-4" role="img" aria-label={`Ejemplo de conversación: ${chat.title}`}>
              {chat.messages.map((m, i) => (
                <p
                  key={i}
                  className={`max-w-[85%] whitespace-pre-line rounded-xl px-3 py-2 text-sm shadow-sm ${
                    m.from === "user"
                      ? "self-end bg-[#d9fdd3]"
                      : "self-start bg-white"
                  }`}
                >
                  {m.text}
                </p>
              ))}
            </div>
          </figure>
        ))}
      </div>
    </section>
  );
}
