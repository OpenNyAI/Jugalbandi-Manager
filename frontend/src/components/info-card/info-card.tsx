import './info-card.css'

interface IInfoCardProps {
  title: string;
  className: string;
}

function InfoCard(props: IInfoCardProps) {
  const { title, className } = props;

  return (
    <div className={className ? `${className} card`: 'card'}>
      <div className='card-img'></div>
      <div className='card-title'>{title}</div>
    </div>
  );
}

export default InfoCard;