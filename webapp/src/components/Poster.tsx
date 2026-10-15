type Props = { url: string | null; title: string; className?: string };

export default function Poster({ url, title, className = "" }: Props) {
  if (!url) {
    return (
      <div
        className={`flex aspect-[2/3] items-center justify-center rounded-lg bg-zinc-800 p-2 text-center text-sm text-zinc-400 ${className}`}
      >
        {title}
      </div>
    );
  }
  return (
    <img
      src={url}
      alt={`Affiche de ${title}`}
      loading="lazy"
      className={`aspect-[2/3] w-full rounded-lg object-cover ${className}`}
    />
  );
}
